import os
from html import escape


SERVICE_STAGE = os.getenv("SERVICE_STAGE", "").strip() or "beta"
SERVICE_STAGE_LABELS = {
    "development": "開発中",
    "beta": "無料ベータ・課金未開始",
    "production": "正式版",
}

GENERAL_DISCLAIMER = (
    "本サービスは一般的な市場情報と分析結果を提供するもので、"
    "特定の金融商品の売買を勧誘・推奨するものではありません。"
    "投資判断はご自身の責任で行ってください。"
)

PERFORMANCE_DISCLAIMER = (
    "表示する実績やバックテストは将来の成果を保証しません。"
    "手数料、税金、価格差などにより実際の結果は異なります。"
)


def service_stage_label():
    return SERVICE_STAGE_LABELS.get(SERVICE_STAGE, SERVICE_STAGE)


def env_enabled(name):
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def premium_preview_html():
    signup_url = os.getenv("PREMIUM_SIGNUP_URL", "").strip()
    if signup_url:
        action = (
            f'<a class="premium-button" href="{escape(signup_url, quote=True)}">'
            "先行案内に登録</a>"
        )
    else:
        action = '<span class="premium-status">準備中・課金未開始</span>'

    return f"""
    <section class="card premium-card" aria-labelledby="premium-title">
        <div>
            <span class="premium-label">PREMIUM</span>
            <h2 id="premium-title">より深い分析と会員限定通知</h2>
            <p>日次の詳細分析、変化点の解説、会員限定LINE通知を準備しています。</p>
            <p class="data-note">法務・精度・会員配信の公開基準を満たすまで課金は開始しません。</p>
        </div>
        {action}
    </section>
    """


def adsense_html():
    if not env_enabled("ADS_ENABLED"):
        return ""

    client = os.getenv("ADSENSE_CLIENT", "").strip()
    slot = os.getenv("ADSENSE_SLOT", "").strip()
    if not client or not slot:
        return ""

    safe_client = escape(client, quote=True)
    safe_slot = escape(slot, quote=True)
    return f"""
    <aside class="ad-card" aria-label="広告">
        <span class="ad-label">広告</span>
        <ins class="adsbygoogle" style="display:block"
             data-ad-client="{safe_client}"
             data-ad-slot="{safe_slot}"
             data-ad-format="auto" data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </aside>
    <script async crossorigin="anonymous"
      src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={safe_client}"></script>
    """
