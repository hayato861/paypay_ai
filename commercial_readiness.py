import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from validation import evaluate_backtest, evaluate_ml, passes_adoption_gate


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def env_present(name):
    return bool(os.getenv(name, "").strip())


def run_checks():
    checks = [
        Check(
            "legal_review",
            os.getenv("LEGAL_REVIEW_APPROVED", "").lower() == "true",
            "日本の金融規制に詳しい専門家の確認が必要",
        ),
        Check("terms_url", env_present("TERMS_URL"), "利用規約URLが必要"),
        Check("privacy_url", env_present("PRIVACY_URL"), "プライバシーポリシーURLが必要"),
        Check("support_email", env_present("SUPPORT_EMAIL"), "問い合わせ窓口が必要"),
        Check(
            "paid_launch_switch",
            os.getenv("PAID_LAUNCH_ENABLED", "").lower() == "true",
            "正式公開時だけ明示的に有効化する",
        ),
        Check(
            "checkout_url",
            env_present("STRIPE_CHECKOUT_URL"),
            "Stripe Checkout URLが必要",
        ),
        Check(
            "member_session_secret",
            env_present("MEMBER_SESSION_SECRET"),
            "推測困難な会員セッション署名鍵が必要",
        ),
        Check(
            "production_email_delivery",
            os.getenv("MAGIC_LINK_DELIVERY") == "smtp",
            "本番ログインリンクはconsoleではなくSMTP配信が必要",
        ),
        Check(
            "stripe_configuration",
            all(
                env_present(name)
                for name in ("STRIPE_SECRET_KEY", "STRIPE_PRICE_ID", "STRIPE_WEBHOOK_SECRET")
            ),
            "Stripeの本番キー、Price ID、Webhook secretが必要",
        ),
        Check(
            "paid_line_delivery",
            os.getenv("LINE_DELIVERY_MODE") in {"push", "audience"},
            "broadcastでは有料会員を分離できない",
        ),
        Check(
            "generated_assets",
            all(
                Path(path).exists()
                for path in ("index.html", "data/market_report.png", "data/x_post.txt")
            ),
            "HTML、画像、X原稿が必要",
        ),
    ]

    model_specs = [
        ("course_model", evaluate_backtest),
        ("ml_v1", lambda: evaluate_ml("data/ml_test.csv", "probability_up")),
        ("ml_v2", lambda: evaluate_ml("data/ml_test_v2.csv", "up_probability")),
    ]

    for name, evaluator in model_specs:
        try:
            result = evaluator()
            checks.append(
                Check(
                    name,
                    passes_adoption_gate(result),
                    f"edge={result['edge']:+.1%}, samples={result['samples']}",
                )
            )
        except (FileNotFoundError, ValueError, KeyError) as error:
            checks.append(Check(name, False, f"検証不能: {error}"))

    return checks


def report(checks):
    ready = all(check.passed for check in checks)
    return {
        "ready_for_paid_launch": ready,
        "checks": [asdict(check) for check in checks],
    }


def main():
    result = report(run_checks())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ready_for_paid_launch"] else 1)


if __name__ == "__main__":
    main()
