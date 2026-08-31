import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import member_store as store
from member_app import create_app
from stripe_test_setup import create_test_product
from membership_config_check import checks as membership_checks


class MembershipTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {
            "MEMBER_DB_PATH": str(Path(self.directory.name) / "members.db"),
            "MEMBER_SESSION_SECRET": "test-secret",
            "SERVICE_STAGE": "development",
            "MAGIC_LINK_DELIVERY": "console",
            "STRIPE_SECRET_KEY": "sk_test_example",
            "STRIPE_PRICE_ID": "price_test",
            "STRIPE_WEBHOOK_SECRET": "whsec_test",
            "PREMIUM_REPORT_OUTPUT": str(Path(self.directory.name) / "premium.html"),
        }, clear=True)
        self.env.start()
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def tearDown(self):
        self.env.stop()
        self.directory.cleanup()

    def csrf(self):
        response = self.client.get("/login")
        return re.search(r'name="csrf" value="([^"]+)', response.get_data(as_text=True)).group(1)

    def login(self):
        captured = {}
        with patch("member_app.send_login_link", side_effect=lambda email, link: (captured.update(link=link), "console")[1]):
            response = self.client.post("/login", data={"email": "Member@example.com", "csrf": self.csrf()})
        self.assertEqual(response.status_code, 200)
        return self.client.get(captured["link"].split("?", 1)[1].join(["/verify?", ""]), follow_redirects=True)

    def test_magic_link_login_is_one_time_and_normalizes_email(self):
        captured = {}
        with patch("member_app.send_login_link", side_effect=lambda email, link: (captured.update(link=link), "console")[1]):
            response = self.client.post("/login", data={"email": "Member@Example.COM", "csrf": self.csrf()})
        path = "/verify?" + captured["link"].split("?", 1)[1]
        first = self.client.get(path, follow_redirects=True)
        second = self.client.get(path)
        self.assertIn("member@example.com", first.get_data(as_text=True))
        self.assertEqual(second.status_code, 400)
        self.assertIn("ターミナルを確認", response.get_data(as_text=True))

    def test_login_rejects_malformed_email(self):
        response = self.client.post(
            "/login", data={"email": "bad\n@example.com", "csrf": self.csrf()}
        )
        self.assertEqual(response.status_code, 400)

    def test_paid_report_requires_active_subscription(self):
        self.login()
        self.assertEqual(self.client.get("/members/report").status_code, 403)
        member = store.get_or_create_member("member@example.com")
        store.set_customer(member["id"], "cus_test")
        store.update_subscription("cus_test", "active")
        Path(os.environ["PREMIUM_REPORT_OUTPUT"]).write_text("PRIVATE REPORT", encoding="utf-8")
        response = self.client.get("/members/report")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PRIVATE REPORT", response.get_data(as_text=True))

    def test_active_member_sees_clear_message_before_report_generation(self):
        self.login()
        member = store.get_or_create_member("member@example.com")
        store.set_customer(member["id"], "cus_test")
        store.update_subscription("cus_test", "active")
        response = self.client.get("/members/report")
        self.assertEqual(response.status_code, 503)
        self.assertIn("レポート準備中", response.get_data(as_text=True))

    @patch("member_app.stripe.Webhook.construct_event")
    def test_signed_webhook_updates_and_is_idempotent(self, construct):
        member = store.get_or_create_member("member@example.com")
        store.set_customer(member["id"], "cus_test")
        construct.return_value = {
            "id": "evt_1", "type": "customer.subscription.updated",
            "data": {"object": {"customer": "cus_test", "status": "active", "current_period_end": 123}},
        }
        self.client.post("/stripe/webhook", data=b"payload", headers={"Stripe-Signature": "sig"})
        self.client.post("/stripe/webhook", data=b"payload", headers={"Stripe-Signature": "sig"})
        self.assertEqual(store.get_member(member["id"])["subscription_status"], "active")
        self.assertTrue(store.event_processed("evt_1"))

    @patch("member_app.stripe.checkout.Session.create")
    @patch("member_app.stripe.Customer.create")
    def test_checkout_uses_subscription_mode(self, customer_create, session_create):
        self.login()
        customer_create.return_value = Mock(id="cus_test")
        session_create.return_value = Mock(url="https://checkout.stripe.test/session")
        account = self.client.get("/account").get_data(as_text=True)
        csrf = re.search(r'name="csrf" value="([^"]+)', account).group(1)
        response = self.client.post("/billing/checkout", data={"csrf": csrf})
        self.assertEqual(response.status_code, 303)
        self.assertEqual(session_create.call_args.kwargs["mode"], "subscription")
        self.assertEqual(session_create.call_args.kwargs["line_items"][0]["price"], "price_test")

    def test_stripe_product_setup_is_dry_run_by_default(self):
        result = create_test_product(980)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["monthly_yen"], 980)

    def test_health_check_does_not_require_login(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_membership_configuration_can_be_checked_without_printing_secrets(self):
        with patch.dict(os.environ, {
            "MEMBER_SESSION_SECRET": "x" * 48,
            "STRIPE_SECRET_KEY": "sk_test_hidden_but_long_enough",
            "STRIPE_PRICE_ID": "price_test_long_enough",
            "STRIPE_WEBHOOK_SECRET": "whsec_test_long_enough",
            "MEMBER_DB_PATH": str(Path(self.directory.name) / "members.db"),
            "SERVICE_STAGE": "development",
        }, clear=True):
            result = membership_checks()
        self.assertTrue(all(passed for _, passed, _ in result))
        self.assertNotIn("sk_test_hidden", repr(result))


if __name__ == "__main__":
    unittest.main()
