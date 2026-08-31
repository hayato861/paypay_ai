import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def database_path():
    return Path(os.getenv("MEMBER_DB_PATH", "data/members.db"))


@contextmanager
def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS members (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT NOT NULL UNIQUE,
          stripe_customer_id TEXT UNIQUE,
          subscription_status TEXT NOT NULL DEFAULT 'inactive',
          current_period_end INTEGER,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS login_tokens (
          token_hash TEXT PRIMARY KEY,
          member_id INTEGER NOT NULL,
          expires_at INTEGER NOT NULL,
          used_at INTEGER,
          FOREIGN KEY(member_id) REFERENCES members(id)
        );
        CREATE TABLE IF NOT EXISTS stripe_events (
          event_id TEXT PRIMARY KEY,
          processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)


def get_or_create_member(email):
    normalized = email.strip().lower()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO members(email) VALUES (?)", (normalized,))
        return db.execute("SELECT * FROM members WHERE email = ?", (normalized,)).fetchone()


def get_member(member_id):
    with connect() as db:
        return db.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()


def get_member_by_customer(customer_id):
    with connect() as db:
        return db.execute(
            "SELECT * FROM members WHERE stripe_customer_id = ?", (customer_id,)
        ).fetchone()


def set_customer(member_id, customer_id):
    with connect() as db:
        db.execute(
            "UPDATE members SET stripe_customer_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (customer_id, member_id),
        )


def save_login_token(member_id, token_hash, expires_at):
    with connect() as db:
        db.execute(
            "INSERT INTO login_tokens(token_hash,member_id,expires_at) VALUES (?,?,?)",
            (token_hash, member_id, expires_at),
        )


def consume_login_token(token_hash, now):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM login_tokens WHERE token_hash=? AND used_at IS NULL AND expires_at>=?",
            (token_hash, now),
        ).fetchone()
        if not row:
            return None
        db.execute("UPDATE login_tokens SET used_at=? WHERE token_hash=?", (now, token_hash))
        return row["member_id"]


def event_processed(event_id):
    with connect() as db:
        return db.execute(
            "SELECT 1 FROM stripe_events WHERE event_id=?", (event_id,)
        ).fetchone() is not None


def mark_event_processed(event_id):
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO stripe_events(event_id) VALUES (?)", (event_id,))


def update_subscription(customer_id, status, period_end=None):
    with connect() as db:
        db.execute(
            """UPDATE members SET subscription_status=?, current_period_end=?,
               updated_at=CURRENT_TIMESTAMP WHERE stripe_customer_id=?""",
            (status, period_end, customer_id),
        )


def has_paid_access(member):
    return bool(member and member["subscription_status"] in {"active", "trialing"})
