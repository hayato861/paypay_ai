import os
from html import escape
from pathlib import Path

from clock import now_jst
from history import average_score, yesterday_diff
from service import GENERAL_DISCLAIMER, PERFORMANCE_DISCLAIMER


def create_premium_report_page(
    data,
    market_score,
    ranking,
    reasons,
    insight,
    output=None,
):
    """Generate the private member report. Never place output under public pages."""
    output = Path(
        output
        or os.getenv("PREMIUM_REPORT_OUTPUT", "data/private/premium_report.html")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    delta = yesterday_diff()
    average = average_score(7)
    delta_text = "—" if delta is None else f"{delta:+}点"
    average_text = "—" if average is None else f"{average:.1f}点"
    risk_items = []
    risk_points = 0
    if data["vix"] >= 25:
        risk_items.append(f"VIX {data['vix']:.2f}：高警戒。市場変動の拡大に注意")
        risk_points += 2
    elif data["vix"] >= 20:
        risk_items.append(f"VIX {data['vix']:.2f}：注意水準")
        risk_points += 1
    else:
        risk_items.append(f"VIX {data['vix']:.2f}：現在は低位")
    if abs(data["change"]) >= 2:
        risk_items.append(f"QQQ {data['change']:+.2f}%：日次変動が大きい状態")
        risk_points += 2
    elif abs(data["change"]) >= 1:
        risk_items.append(f"QQQ {data['change']:+.2f}%：通常より値動きが大きめ")
        risk_points += 1
    else:
        risk_items.append(f"QQQ {data['change']:+.2f}%：日次変動は設定範囲内")
    if delta is None:
        risk_items.append("市場スコア前日差：比較データ不足")
    elif delta <= -10:
        risk_items.append(f"市場スコア前日差 {delta:+}点：急低下を検出")
        risk_points += 2
    else:
        risk_items.append(f"市場スコア前日差 {delta:+}点")
    risk_level = "高" if risk_points >= 4 else "中" if risk_points >= 2 else "低"
    risk_class = "high" if risk_points >= 4 else "medium" if risk_points >= 2 else "low"

    ranking_rows = "".join(
        f"<tr><td>{index}</td><td>{escape(course)}</td><td>{score}点</td></tr>"
        for index, (course, score) in enumerate(ranking, start=1)
    )
    analysis_items = "".join(
        f"<li>{escape(item)}</li>" for item in [*reasons, *insight]
    ) or "<li>追加の変化要因はありません</li>"
    risk_html = "".join(f"<li>{escape(item)}</li>" for item in risk_items)
    updated_at = now_jst().strftime("%Y-%m-%d %H:%M JST")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <title>PayPay AI Premium Report</title>
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
<main class="container member-report">
  <header class="card member-header">
    <span class="premium-label">MEMBERS ONLY</span>
    <h1>Premium Daily Analysis</h1>
    <p class="data-note">更新日時：{updated_at}</p>
  </header>
  <section class="premium-metrics">
    <article class="card"><span>市場スコア</span><strong>{market_score}</strong></article>
    <article class="card"><span>前日比</span><strong>{delta_text}</strong></article>
    <article class="card"><span>7日平均</span><strong>{average_text}</strong></article>
  </section>
  <section class="plan-grid">
    <article class="card"><h2>変化点と背景</h2><ul>{analysis_items}</ul></article>
    <article class="card risk-card"><h2>リスク監視 <span class="risk-level {risk_class}">警戒度 {risk_level}</span></h2><ul>{risk_html}</ul></article>
  </section>
  <section class="card"><h2>コース比較</h2><div class="table-scroll"><table><tbody>{ranking_rows}</tbody></table></div></section>
  <section class="card"><h2>主要市場データ</h2><div class="premium-data-grid">
    <span>QQQ <strong>{data['change']:+.2f}%</strong></span>
    <span>S&amp;P500 <strong>{data['spy_change']:+.2f}%</strong></span>
    <span>VIX <strong>{data['vix']:.2f}</strong></span>
  </div></section>
  <section class="card compliance-card"><p>{escape(GENERAL_DISCLAIMER)}</p><p>{escape(PERFORMANCE_DISCLAIMER)}</p></section>
</main>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
    return output
