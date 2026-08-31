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


def create_test_product(monthly_yen, confirm=False):
    if monthly_yen < 100:
        raise ValueError("月額は100円以上で指定してください")
    if not confirm:
        return {
            "dry_run": True,
            "product": "PayPay AI Premium (Test)",
            "monthly_yen": monthly_yen,
        }
    require_test_key()
    product = stripe.Product.create(
        name="PayPay AI Premium (Test)",
        description="詳細な市場分析と会員限定LINE通知（テスト環境）",
        metadata={"environment": "test"},
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=monthly_yen,
        currency="jpy",
        recurring={"interval": "month"},
        metadata={"environment": "test"},
    )
    return {"dry_run": False, "product_id": product.id, "price_id": price.id}


def main():
    parser = argparse.ArgumentParser(description="Stripeテスト商品を安全に作成")
    parser.add_argument("--monthly-yen", type=int, default=980)
    parser.add_argument(
        "--confirm-create-test-product",
        action="store_true",
        help="指定した場合だけStripeテスト環境へ商品を作成",
    )
    args = parser.parse_args()
    print(json.dumps(
        create_test_product(args.monthly_yen, args.confirm_create_test_product),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
