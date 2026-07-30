from pathlib import Path
from datetime import datetime

from stats import get_stats


def create_page(
    data,
    market_score,
    ranking,
    reasons,
    insight
):

    stats = get_stats()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

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

    top_course = ranking[0][0]
    top_score = ranking[0][1]

    qqq_color = "#22c55e" if data["change"] >= 0 else "#ef4444"
    spy_color = "#22c55e" if data["spy_change"] >= 0 else "#ef4444"

    reason_html = ""

    for reason in reasons:
        reason_html += f"<li>{reason}</li>"

    insight_html = ""

    for item in insight:
        insight_html += f"<li>{item}</li>"

    ranking_html = ""

    medals = ["🥇", "🥈", "🥉"]

    for i, (course, score) in enumerate(ranking):

        if i < 3:
            icon = medals[i]
        else:
            icon = f"{i+1}."

        ranking_html += f"""
        <tr>
            <td>{icon}</td>
            <td>{course}</td>
            <td>{score}点</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>PayPay AI</title>

<link rel="stylesheet" href="css/style.css">

</head>

<body>

<div class="container">

<div class="card header-card">

<h1>
📈 PayPay AI
</h1>

<div class="subtitle">
毎朝7:30 自動更新
</div>

<div class="small">
更新日時：{now}
</div>

</div>


<div class="grid">

<div class="card">

<div class="small">
市場スコア
</div>

<div class="score">
{market_score}
</div>

<div class="market">
{stars}
</div>

</div>

<div class="card">

<div class="small">
今日のおすすめ
</div>

<h2>
🥇 {top_course}
</h2>

<p>
{top_score}点
</p>

</div>

<div class="card">

<div class="small">
AI実績
</div>

<p>

勝率 {stats["win_rate"]}%<br>
予想 {stats["total"]}回<br>
勝ち {stats["win"]}<br>
負け {stats["lose"]}

</p>

</div>

</div>

<div class="card">

<h2>
📊 市場データ
</h2>

<table>

<tr>

<td>QQQ</td>

<td style="color:{qqq_color}">

{data["change"]:+.2f}%

</td>

</tr>

<tr>

<td>S&P500</td>

<td style="color:{spy_color}">

{data["spy_change"]:+.2f}%

</td>

</tr>

<tr>

<td>VIX</td>

<td>{data["vix"]:.2f}</td>

</tr>

</table>

</div>

<div class="card">

<h2>📈 市場スコアとは？</h2>

<p>

<strong>市場スコア</strong>は、PayPay AIが毎朝マーケットを分析して算出する
<strong>100点満点の独自評価</strong>です。

</p>

<table>

<tr>
<td>80〜100</td>
<td>★★★★★ 強気相場</td>
</tr>

<tr>
<td>60〜79</td>
<td>★★★★☆ やや強気</td>
</tr>

<tr>
<td>40〜59</td>
<td>★★★☆☆ 中立</td>
</tr>

<tr>
<td>20〜39</td>
<td>★★☆☆☆ やや弱気</td>
</tr>

<tr>
<td>0〜19</td>
<td>★☆☆☆☆ 弱気</td>
</tr>

</table>

<p class="small">

※ QQQ・S&P500・VIXなどをもとにAIが毎朝判定しています。

</p>

</div>

<ul>

{insight_html}

</ul>

<div class="card">

<h2>🏆 おすすめランキング</h2>

<table>

{ranking_html}

</table>

</div>

<footer>

Powered by PayPay AI

</footer>

</div>

</body>

</html>
"""

    output = Path("index.html")

    output.write_text(
        html,
        encoding="utf-8"
    )

    print("保存先:", output.resolve())