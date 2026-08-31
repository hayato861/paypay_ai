import os
from pathlib import Path

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String, Table, Text, create_engine, func, inspect, select, update
from sqlalchemy.exc import IntegrityError

metadata = MetaData()
members = Table("members", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(254), nullable=False, unique=True),
    Column("stripe_customer_id", String(255), unique=True),
    Column("subscription_status", String(32), nullable=False, server_default="inactive"),
    Column("current_period_end", Integer),
    Column("cancel_at_period_end", Boolean, nullable=False, server_default="false"),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now()))
login_tokens = Table("login_tokens", metadata,
    Column("token_hash", String(64), primary_key=True),
    Column("member_id", Integer, ForeignKey("members.id"), nullable=False),
    Column("expires_at", Integer, nullable=False), Column("used_at", Integer))
stripe_events = Table("stripe_events", metadata,
    Column("event_id", String(255), primary_key=True),
    Column("processed_at", DateTime, nullable=False, server_default=func.now()))
premium_reports = Table("premium_reports", metadata,
    Column("report_date", String(10), primary_key=True),
    Column("html", Text, nullable=False),
    Column("created_at", DateTime, nullable=False, server_default=func.now()))
_engines = {}


def database_url():
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        if value.startswith("postgres://"):
            value = "postgresql+psycopg://" + value.removeprefix("postgres://")
        elif value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value
    path = Path(os.getenv("MEMBER_DB_PATH", "data/members.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.resolve()}"


def engine():
    url = database_url()
    if url not in _engines:
        _engines[url] = create_engine(url, pool_pre_ping=True)
    return _engines[url]


def initialize():
    db_engine = engine()
    metadata.create_all(db_engine)
    columns = {column["name"] for column in inspect(db_engine).get_columns("members")}
    if "cancel_at_period_end" not in columns:
        with db_engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE members ADD COLUMN cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE")


def _member(connection, statement):
    row = connection.execute(statement).mappings().first()
    return dict(row) if row else None


def get_or_create_member(email):
    normalized = email.strip().lower()
    try:
        with engine().begin() as connection:
            connection.execute(members.insert().values(email=normalized))
    except IntegrityError:
        pass
    with engine().connect() as connection:
        return _member(connection, select(members).where(members.c.email == normalized))


def get_member(member_id):
    with engine().connect() as connection:
        return _member(connection, select(members).where(members.c.id == member_id))


def get_member_by_customer(customer_id):
    with engine().connect() as connection:
        return _member(connection, select(members).where(members.c.stripe_customer_id == customer_id))


def set_customer(member_id, customer_id):
    with engine().begin() as connection:
        connection.execute(update(members).where(members.c.id == member_id).values(stripe_customer_id=customer_id, updated_at=func.now()))


def save_login_token(member_id, token_hash, expires_at):
    with engine().begin() as connection:
        connection.execute(login_tokens.insert().values(token_hash=token_hash, member_id=member_id, expires_at=expires_at))


def consume_login_token(token_hash, now):
    with engine().begin() as connection:
        row = connection.execute(select(login_tokens).where(login_tokens.c.token_hash == token_hash, login_tokens.c.used_at.is_(None), login_tokens.c.expires_at >= now)).mappings().first()
        if not row:
            return None
        connection.execute(update(login_tokens).where(login_tokens.c.token_hash == token_hash).values(used_at=now))
        return row["member_id"]


def event_processed(event_id):
    with engine().connect() as connection:
        return connection.execute(select(stripe_events.c.event_id).where(stripe_events.c.event_id == event_id)).first() is not None


def mark_event_processed(event_id):
    try:
        with engine().begin() as connection:
            connection.execute(stripe_events.insert().values(event_id=event_id))
    except IntegrityError:
        pass


def update_subscription(customer_id, status, period_end=None, cancel_at_period_end=False):
    with engine().begin() as connection:
        connection.execute(update(members).where(members.c.stripe_customer_id == customer_id).values(
            subscription_status=status, current_period_end=period_end,
            cancel_at_period_end=bool(cancel_at_period_end), updated_at=func.now()))


def save_premium_report(report_date, html):
    with engine().begin() as connection:
        existing = connection.execute(
            select(premium_reports.c.report_date).where(
                premium_reports.c.report_date == report_date
            )
        ).first()
        if existing:
            connection.execute(
                update(premium_reports)
                .where(premium_reports.c.report_date == report_date)
                .values(html=html, created_at=func.now())
            )
        else:
            connection.execute(
                premium_reports.insert().values(report_date=report_date, html=html)
            )


def latest_premium_report():
    with engine().connect() as connection:
        row = connection.execute(
            select(premium_reports)
            .order_by(premium_reports.c.report_date.desc())
            .limit(1)
        ).mappings().first()
        return dict(row) if row else None


def has_paid_access(member):
    return bool(member and member["subscription_status"] in {"active", "trialing"})
