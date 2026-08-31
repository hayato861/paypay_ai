import os


SERVICE_STAGE = os.getenv("SERVICE_STAGE", "beta")
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
