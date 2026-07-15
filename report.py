def create_report(data, market_score, reasons, ranking):
    
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

📊 市場データ
QQQ      : {data['change']:+.2f}%
S&P500   : {data['spy_change']:+.2f}%
VIX      : {data['vix']:.2f}

━━━━━━━━━━━━━━

🧠 AI分析
"""

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