import argparse
import json
import os

import stripe
from dotenv import load_dotenv

load_dotenv()


def require_test_key():
    key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if not key.startswith("sk_test_"):
        raise RuntimeError("Stripeテストキー（sk_test_...）だけ使用できます")
    stripe.api_key = key


def create_test_portal(confirm=False):
    plan = {
        "payment_method_update": True,
        "invoice_history": True,
        "subscription_cancel": "at_period_end",
    }
    if not confirm:
        return {"dry_run": True, "features": plan}
    require_test_key()
    configuration = stripe.billing_portal.Configuration.create(
        features={
            "payment_method_update": {"enabled": True},
            "invoice_history": {"enabled": True},
            "subscription_cancel": {
                "enabled": True,
                "mode": "at_period_end",
                "proration_behavior": "none",
            },
        },
        metadata={"service": "paypay_ai", "environment": "test"},
    )
    return {"dry_run": False, "configuration_id": configuration.id}


def main():
    parser = argparse.ArgumentParser(description="Stripe SandboxのCustomer Portalを設定")
    parser.add_argument("--confirm-create-test-portal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        create_test_portal(args.confirm_create_test_portal),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()

