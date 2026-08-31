from stats import get_stats

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

    report = f"""📈 PayPay AI Morning Report

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
    report += "🤖 Powered by PayPay AI"

    return report
