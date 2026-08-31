import os
from html import escape
from pathlib import Path

from service import GENERAL_DISCLAIMER, PERFORMANCE_DISCLAIMER, env_enabled


def _link(url, label):
    if not url:
        return ""
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def create_premium_page(output=Path("premium.html")):
    price = os.getenv("PREMIUM_PRICE_LABEL", "月額料金未定").strip()
    checkout_url = os.getenv("STRIPE_CHECKOUT_URL", "").strip()
    signup_url = os.getenv("PREMIUM_SIGNUP_URL", "").strip()
    can_sell = (
        env_enabled("PAID_LAUNCH_ENABLED")
        and env_enabled("LEGAL_REVIEW_APPROVED")
        and bool(checkout_url)
    )

    if can_sell:
        action = _link(checkout_url, "プレミアムを始める")
        action_class = "premium-button"
    elif signup_url:
        action = _link(signup_url, "先行案内に登録")
        action_class = "premium-button"
    else:
        action = "準備中・課金未開始"
        action_class = "premium-status"

    terms = _link(os.getenv("TERMS_URL", "").strip(), "利用規約")
    privacy = _link(os.getenv("PRIVACY_URL", "").strip(), "プライバシーポリシー")
    legal_links = " ｜ ".join(link for link in (terms, privacy) if link)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PayPay AI Premium</title>
    <meta name="description" content="PayPay AI Premiumの詳細分析と会員限定LINE通知">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<main class="container premium-page">
    <a class="back-link" href="index.html">← 無料レポートへ戻る</a>
    <section class="card premium-hero">
        <span class="premium-label">PAYPAY AI PREMIUM</span>
        <h1>数字だけで終わらない、毎朝の市場分析</h1>
        <p>無料版の市場サマリーに加え、変化点、7日傾向、警戒条件を整理して個別LINEへ届けます。</p>
        <div class="premium-price">{escape(price)}</div>
        <div class="{action_class}">{action}</div>
    </section>

    <section class="plan-grid">
        <article class="card">
            <h2>無料版</h2>
            <ul><li>毎朝の市場スコア</li><li>公開ランキングと市場データ</li><li>モデル検証結果</li><li>広告あり（審査通過後）</li></ul>
        </article>
        <article class="card premium-plan">
            <h2>プレミアム</h2>
            <ul><li>前日差と7日平均の詳細分析</li><li>市場の変化要因とリスク監視</li><li>会員限定LINE個別通知</li><li>広告なし</li></ul>
        </article>
    </section>

    <section class="card compliance-card">
        <h2>提供開始について</h2>
        <p>法務確認、モデル採用基準、会員認証、課金・解約処理、配信試験が完了するまで課金を開始しません。</p>
        <p>{escape(GENERAL_DISCLAIMER)}</p><p>{escape(PERFORMANCE_DISCLAIMER)}</p><p>{legal_links}</p>
    </section>
</main>
</body>
</html>
"""
    output = Path(output)
    output.write_text(html, encoding="utf-8")
    return output

