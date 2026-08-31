import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def present(name):
    return bool(os.getenv(name, "").strip())


def looks_real(value, prefix):
    return value.startswith(prefix) and len(value) > len(prefix) + 8 and "..." not in value


def checks():
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    return [
        ("member_session_secret", len(os.getenv("MEMBER_SESSION_SECRET", "")) >= 32, "32文字以上のランダム値"),
        ("stripe_test_key", looks_real(stripe_key, "sk_test_"), "sk_test_で始まるテスト秘密鍵"),
        ("stripe_price", looks_real(os.getenv("STRIPE_PRICE_ID", ""), "price_"), "price_で始まる月額Price ID"),
        ("stripe_webhook", looks_real(os.getenv("STRIPE_WEBHOOK_SECRET", ""), "whsec_"), "whsec_で始まる署名シークレット"),
        ("database_parent", Path(os.getenv("MEMBER_DB_PATH", "data/members.db")).parent.exists(), "DB保存先ディレクトリ"),
        ("development_mode", os.getenv("SERVICE_STAGE", "development") == "development", "初回試験はdevelopment"),
    ]


def main():
    result = [
        {"name": name, "passed": passed, "required": detail}
        for name, passed, detail in checks()
    ]
    print(json.dumps({"ready": all(item["passed"] for item in result), "checks": result}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(item["passed"] for item in result) else 1)


if __name__ == "__main__":
    main()
