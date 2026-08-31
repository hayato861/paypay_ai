import hashlib
import os
import re
import secrets
import smtplib
import time
from email.message import EmailMessage
from functools import wraps
from html import escape
from pathlib import Path

import stripe
from stripe._error import SignatureVerificationError
from flask import Flask, abort, redirect, request, send_from_directory, session
from dotenv import load_dotenv

import member_store as store

load_dotenv()


def _required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}が設定されていません")
    return value


def _page(title, body):
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title}</title><link rel="stylesheet" href="/css/style.css"></head>
    <body><main class="container member-auth"><section class="card"><h1>{title}</h1>{body}</section></main></body></html>"""


def send_login_link(email, link):
    if os.getenv("MAGIC_LINK_DELIVERY", "console") == "console":
        if os.getenv("SERVICE_STAGE", "development") != "development":
            raise RuntimeError("console認証リンクはdevelopmentでのみ使用できます")
        print(f"MAGIC LINK for {email}: {link}")
        return "console"
    message = EmailMessage()
    message["Subject"] = "PayPay AI ログインリンク"
    message["From"] = _required("SMTP_FROM")
    message["To"] = email
    message.set_content(f"15分以内にこちらからログインしてください。\n{link}")
    with smtplib.SMTP_SSL(_required("SMTP_HOST"), int(os.getenv("SMTP_PORT", "465"))) as smtp:
        smtp.login(_required("SMTP_USERNAME"), _required("SMTP_PASSWORD"))
        smtp.send_message(message)
    return "smtp"


def create_app(test_config=None):
    if os.getenv("SERVICE_STAGE") == "production" and not os.getenv("MEMBER_SESSION_SECRET", "").strip():
        raise RuntimeError("productionではMEMBER_SESSION_SECRETが必須です")
    app = Flask(__name__, static_folder=None)
    app.config.update(
        SECRET_KEY=os.getenv("MEMBER_SESSION_SECRET", secrets.token_hex(32)),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("SERVICE_STAGE") == "production",
    )
    if test_config:
        app.config.update(test_config)
    store.initialize()

    def current_member():
        return store.get_member(session.get("member_id")) if session.get("member_id") else None

    def login_required(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if not current_member():
                return redirect("/login")
            return function(*args, **kwargs)
        return wrapped

    def csrf_token():
        session.setdefault("csrf", secrets.token_urlsafe(24))
        return session["csrf"]

    def check_csrf():
        if not secrets.compare_digest(session.get("csrf", ""), request.form.get("csrf", "")):
            abort(400)

    @app.get("/css/<path:filename>")
    def styles(filename):
        return send_from_directory("css", filename)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "service": "paypay-ai-members"}

    @app.get("/login")
    def login():
        return _page("会員ログイン", f'''<p>メールアドレスへログインリンクを送ります。</p>
        <form method="post"><input type="hidden" name="csrf" value="{csrf_token()}">
        <input type="email" name="email" required autocomplete="email">
        <button class="premium-button" type="submit">ログインリンクを送る</button></form>''')

    @app.post("/login")
    def request_login():
        check_csrf()
        email = request.form.get("email", "").strip().lower()
        if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}", email):
            abort(400)
        member = store.get_or_create_member(email)
        token = secrets.token_urlsafe(32)
        store.save_login_token(member["id"], hashlib.sha256(token.encode()).hexdigest(), int(time.time()) + 900)
        delivery = send_login_link(email, request.url_root.rstrip("/") + "/verify?token=" + token)
        if delivery == "console":
            return _page(
                "ターミナルを確認してください",
                "<p>開発モードです。member_app.pyを起動しているターミナルに、有効期限15分のMAGIC LINKを表示しました。</p>",
            )
        return _page("メールを確認してください", "<p>有効期限15分のログインリンクを送信しました。</p>")

    @app.get("/verify")
    def verify():
        token = request.args.get("token", "")
        member_id = store.consume_login_token(hashlib.sha256(token.encode()).hexdigest(), int(time.time()))
        if not member_id:
            abort(400)
        session.clear()
        session["member_id"] = member_id
        return redirect("/account")

    @app.get("/account")
    @login_required
    def account():
        member = current_member()
        access = store.has_paid_access(member)
        csrf = csrf_token()
        if access:
            action = f'''<p><a class="premium-button" href="/members/report">会員レポートを見る</a></p>
            <form method="post" action="/billing/portal"><input type="hidden" name="csrf" value="{csrf}">
            <button type="submit">支払い・解約を管理</button></form>'''
        else:
            action = f'''<p>プレミアム契約は現在無効です。</p>
            <form method="post" action="/billing/checkout"><input type="hidden" name="csrf" value="{csrf}">
            <button class="premium-button" type="submit">テスト決済へ進む</button></form>'''
        return _page(
            "マイページ",
            f"<p>{escape(member['email'])}</p><p>契約状態：{escape(member['subscription_status'])}</p>{action}",
        )

    @app.post("/logout")
    def logout():
        check_csrf()
        session.clear()
        return redirect("/login")

    def stripe_key():
        key = _required("STRIPE_SECRET_KEY")
        if not key.startswith("sk_test_") and os.getenv("ALLOW_STRIPE_LIVE") != "true":
            raise RuntimeError("テスト環境ではStripe本番キーを使用できません")
        stripe.api_key = key

    @app.post("/billing/checkout")
    @login_required
    def checkout():
        check_csrf()
        stripe_key()
        member = current_member()
        customer_id = member["stripe_customer_id"]
        if not customer_id:
            customer = stripe.Customer.create(email=member["email"], metadata={"member_id": str(member["id"])})
            customer_id = customer.id
            store.set_customer(member["id"], customer_id)
        checkout_session = stripe.checkout.Session.create(
            mode="subscription", customer=customer_id,
            line_items=[{"price": _required("STRIPE_PRICE_ID"), "quantity": 1}],
            success_url=request.url_root.rstrip("/") + "/account?checkout=success",
            cancel_url=request.url_root.rstrip("/") + "/account?checkout=cancel",
            client_reference_id=str(member["id"]),
        )
        return redirect(checkout_session.url, code=303)

    @app.post("/billing/portal")
    @login_required
    def portal():
        check_csrf()
        stripe_key()
        member = current_member()
        if not member["stripe_customer_id"]:
            abort(400)
        portal_session = stripe.billing_portal.Session.create(
            customer=member["stripe_customer_id"], return_url=request.url_root.rstrip("/") + "/account"
        )
        return redirect(portal_session.url, code=303)

    @app.post("/stripe/webhook")
    def webhook():
        try:
            event = stripe.Webhook.construct_event(
                request.get_data(), request.headers.get("Stripe-Signature", ""), _required("STRIPE_WEBHOOK_SECRET")
            )
        except (ValueError, SignatureVerificationError):
            abort(400)
        if store.event_processed(event["id"]):
            return {"received": True}
        obj = event["data"]["object"]
        if event["type"] in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
            store.update_subscription(obj["customer"], obj["status"], obj.get("current_period_end"))
        elif event["type"] == "invoice.payment_failed":
            store.update_subscription(obj["customer"], "past_due")
        store.mark_event_processed(event["id"])
        return {"received": True}

    @app.get("/members/report")
    @login_required
    def member_report():
        if not store.has_paid_access(current_member()):
            abort(403)
        report_path = Path(os.getenv("PREMIUM_REPORT_OUTPUT", "data/private/premium_report.html"))
        if not report_path.exists():
            abort(503)
        return report_path.read_text(encoding="utf-8")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
