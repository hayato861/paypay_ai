def create_report(data, stars, reasons, action):

    report = []

    report.append("📊 PayPay AI Morning Report")
    report.append("━━━━━━━━━━━━━━━━━━")
    report.append("")
    report.append(f"QQQ {data['price']:.2f} ({data['change']:+.2f}%)")
    report.append(f"S&P500 {data['spy_change']:+.2f}%")
    report.append(f"VIX {data['vix']:.2f}")
    report.append("")
    report.append(f"判定 {stars}")
    report.append("")
    report.append("理由")

    for r in reasons:
        report.append(f"・{r}")

    report.append("")
    report.append(f"🎯 推奨\n{action}")

    return "\n".join(report)