from pathlib import Path
from datetime import datetime

from stats import get_stats


def create_page(
    data,
    market_score,
    ranking,
    reasons
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

<style>

body{{
background:#0f172a;
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
margin:0;
}}

.container{{
max-width:900px;
margin:auto;
padding:20px;
}}

.card{{
background:#1e293b;
border-radius:20px;
padding:20px;
margin-bottom:20px;
box-shadow:0 10px 30px rgba(0,0,0,.35);
}}

h1{{
margin:0;
font-size:40px;
}}

.subtitle{{
color:#94a3b8;
}}

.score{{
font-size:70px;
font-weight:bold;
color:#22c55e;
}}

.grid{{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:15px;
}}

.small{{
font-size:14px;
color:#94a3b8;
}}

.market{{
font-size:30px;
font-weight:bold;
}}

table{{
width:100%;
border-collapse:collapse;
}}

td{{
padding:10px;
border-bottom:1px solid #334155;
}}

ul{{
padding-left:20px;
}}

footer{{
text-align:center;
padding:30px;
color:#94a3b8;
}}

</style>

</head>

<body>

<div class="container">

<div class="card">

<h1>📈 PayPay AI</h1>

<div class="subtitle">

毎朝7:30 自動更新

</div>

<div class="small">

更新日時：{now}

</div>

</div>

<div class="grid">

<div class="card">

<div class="small">市場スコア</div>

<div class="score">{market_score}</div>

<div>{stars}</div>

</div>

<div class="card">

<div class="small">今日のおすすめ</div>

<h2>🥇 {top_course}</h2>

<p>{top_score}点</p>

</div>

<div class="card">

<div class="small">AI実績</div>

<p>

勝率 {stats["win_rate"]}%<br>
予想 {stats["total"]}回<br>
勝ち {stats["win"]}<br>
負け {stats["lose"]}

</p>

</div>

</div>

<div class="card">

<h2>📊 市場データ</h2>

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

<h2>🧠 AI分析</h2>

<ul>

{reason_html}

</ul>

</div>

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

    Path("public/index.html").write_text(
        html,
        encoding="utf-8"
    )

    print("Webページ更新")