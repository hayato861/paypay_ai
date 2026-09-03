from stats import get_stats
from history import average_score, yesterday_diff
from service import GENERAL_DISCLAIMER, PERFORMANCE_DISCLAIMER

def create_report(data, market_score, reasons, ranking, insight):

    stats = get_stats()
    win_rate = "—" if stats["win_rate"] is None else f'{stats["win_rate"]}%'

    # 星評価
    if market_score >= 85:
        stars = "★★★★★"
    elif market_score >= 70:
        stars = "★★★★☆"
    elif market_score >= 55:
        stars = "★★★☆☆"
    elif market_score >= 40:
        stars = "★★☆☆☆"
    else:
        stars = "★☆☆☆☆"

    report = f"""📈 PayPay AI Market Report

市場スコア：{market_score}点
判定：{stars}

━━━━━━━━━━━━━━

📊 AI実績

検証済み：{stats['verified_total']}回
勝ち：{stats['win']}回
負け：{stats['lose']}回
保留：{stats['pending']}回
旧方式（参考）：{stats['legacy']}回
実ETF勝率：{win_rate}

━━━━━━━━━━━━━━

📊 市場データ
QQQ      : {data['change']:+.2f}%
S&P500   : {data['spy_change']:+.2f}%
VIX      : {data['vix']:.2f}

━━━━━━━━━━━━━━

🧠 AI分析
"""

    report += "\n━━━━━━━━━━━━━━\n"

    report += "📌 AIインサイト\n\n"

    for line in insight:

        report += f"・{line}\n"

    if reasons:
        for reason in reasons:
            report += f"・{reason}\n"
    else:
        report += "・市場は中立です。\n"

    report += "\n━━━━━━━━━━━━━━\n"
    report += "🏆 おすすめランキング\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, (course, score) in enumerate(ranking):

        if i < 3:
            mark = medals[i]
        else:
            mark = f"{i+1}."

        report += f"{mark} {course}（{score}点）\n"

    report += "\n━━━━━━━━━━━━━━\n"
    report += "⚠️ ご利用上の注意\n"
    report += GENERAL_DISCLAIMER + "\n"
    report += PERFORMANCE_DISCLAIMER + "\n\n"
    report += "🤖 Powered by PayPay AI"

    return report


def create_premium_report(data, market_score, reasons, ranking, insight):
    """Create the deeper report intended for an authenticated paid channel."""
    delta = yesterday_diff()
    average = average_score(7)
    delta_text = "データ不足" if delta is None else f"{delta:+}点"
    average_text = "データ不足" if average is None else f"{average:.1f}点"
    risk_flags = []
    if data["vix"] >= 25:
        risk_flags.append(f"VIXが{data['vix']:.2f}と高く、値動きの拡大に注意")
    if abs(data["change"]) >= 2:
        risk_flags.append(f"QQQの日次変動が{data['change']:+.2f}%と大きい")
    if not risk_flags:
        risk_flags.append("主要指標に設定済みの強い警戒条件はありません")

    lines = [
        "🔐 PayPay AI Premium Analysis",
        "",
        f"市場スコア：{market_score}点（前日比 {delta_text}）",
        f"7日平均：{average_text}",
        f"最上位：{ranking[0][0]}（{ranking[0][1]}点）",
        "",
        "【変化点・背景】",
        *[f"・{item}" for item in (reasons + insight)],
        "",
        "【リスク監視】",
        *[f"・{item}" for item in risk_flags],
        "",
        GENERAL_DISCLAIMER,
        PERFORMANCE_DISCLAIMER,
    ]
    return "\n".join(lines)
