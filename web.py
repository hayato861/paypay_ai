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

    # ------------------------
    # 市場判定
    # ------------------------

    if market_score >= 85:
        stars = "★★★★★"
        status = "🟢 強気相場"
        comment = "積極運用がおすすめです"

    elif market_score >= 70:
        stars = "★★★★☆"
        status = "🟢 やや強気"
        comment = "押し目買いを検討できます"

    elif market_score >= 55:
        stars = "★★★☆☆"
        status = "🟡 中立"
        comment = "様子を見ながら運用"

    elif market_score >= 40:
        stars = "★★☆☆☆"
        status = "🟠 やや弱気"
        comment = "守りを意識"

    else:
        stars = "★☆☆☆☆"
        status = "🔴 弱気相場"
        comment = "慎重な運用がおすすめ"

    top_course = ranking[0][0]
    top_score = ranking[0][1]

    qqq_color = "#22c55e" if data["change"] >= 0 else "#ef4444"
    spy_color = "#22c55e" if data["spy_change"] >= 0 else "#ef4444"

    # ------------------------
    # AI分析
    # ------------------------

    reason_html = ""

    for reason in reasons:
        reason_html += f"<li>{reason}</li>"

    # ------------------------
    # ランキング
    # ------------------------

    medals = ["🥇", "🥈", "🥉"]

    ranking_html = ""

    for i, (course, score) in enumerate(ranking):

        icon = medals[i] if i < 3 else f"{i+1}."

        ranking_html += f"""
        <div class="rank-card">
            <div class="rank-icon">{icon}</div>

            <div class="rank-name">
                {course}
            </div>

            <div class="rank-score">
                {score}点
            </div>
        </div>
        """
        
        
    html = f"""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>PayPay AI</title>

<style>

*{{
box-sizing:border-box;
}}

body{{
margin:0;
background:#07111f;
color:white;
font-family:-apple-system,BlinkMacSystemFont,sans-serif;
}}

.container{{
max-width:1000px;
margin:auto;
padding:25px;
}}

.hero{{
background:linear-gradient(135deg,#2563eb,#0f766e);
padding:40px;
border-radius:24px;
margin-bottom:25px;
box-shadow:0 20px 40px rgba(0,0,0,.35);
}}

.hero h1{{
margin:0;
font-size:46px;
}}

.hero p{{
opacity:.9;
}}

.button{{
display:inline-block;
margin-top:18px;
padding:14px 24px;
background:#22c55e;
color:white;
text-decoration:none;
border-radius:14px;
font-weight:bold;
transition:.2s;
}}

.button:hover{{
transform:scale(1.03);
}}

.grid{{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:20px;
margin-bottom:25px;
}}

.card{{
background:#132238;
border-radius:20px;
padding:22px;
box-shadow:0 12px 25px rgba(0,0,0,.25);
}}

.title{{
color:#94a3b8;
font-size:14px;
margin-bottom:10px;
}}

.score{{
font-size:72px;
font-weight:bold;
color:#4ade80;
}}

.big{{
font-size:58px;
font-weight:bold;
color:#4ade80;
}}

.market{{
font-size:28px;
font-weight:bold;
}}

table{{
width:100%;
border-collapse:collapse;
}}

td{{
padding:14px;
border-bottom:1px solid #243447;
}}

.rank-card{{
display:flex;
align-items:center;
justify-content:space-between;
padding:16px;
margin-bottom:12px;
background:#1b314f;
border-radius:14px;
}}

.rank-icon{{
font-size:24px;
width:45px;
}}

.rank-name{{
flex:1;
font-size:18px;
}}

.rank-score{{
font-weight:bold;
color:#4ade80;
}}

.info{{
background:#1b314f;
padding:18px;
border-radius:14px;
line-height:1.8;
}}

footer{{
text-align:center;
padding:30px;
color:#94a3b8;
}}

@media(max-width:700px){{

.hero h1{{
font-size:34px;
}}

.score{{
font-size:58px;
}}

.big{{
font-size:44px;
}}

}}

</style>

</head>

<body>

<div class="container">

<div class="hero">

<h1>📈 PayPay AI</h1>

<p>

AIが毎朝マーケットを分析し、
PayPayポイント運用をサポートします。

</p>

<div>

<strong>{status}</strong>

<br>

{comment}

</div>

<a class="button" href="#">

📲 LINEで毎朝受け取る

</a>

</div>

<div class="grid">

<div class="card">

<div class="title">

市場スコア

</div>

<div class="score">

{market_score}

</div>

<div class="market">

{stars}

</div>

<p>

{status}

</p>

</div>

<div class="card">

<div class="title">

今日のおすすめ

</div>

<h2>

🥇 {top_course}

</h2>

<div class="big">

{top_score}

</div>

<p>

AIおすすめコース

</p>

</div>

<div class="card">

<div class="title">

AI実績

</div>

<div class="big">

{stats["win_rate"]}%

</div>

<p>

予想 {stats["total"]}回

<br>

勝ち {stats["win"]}

<br>

負け {stats["lose"]}

</p>

</div>

</div>


<div class="card">

<h2>

📊 市場スコアとは？

</h2>

<div class="info">

PayPay AIが毎朝マーケットを分析して作成する
<strong>100点満点の独自指標</strong>です。

<br><br>

評価対象

<ul>

<li>📈 QQQ（NASDAQ100）</li>

<li>📊 S&P500</li>

<li>😨 VIX（恐怖指数）</li>

</ul>

<strong>

80〜100点

</strong>

積極運用がおすすめ

<br><br>

<strong>

60〜79点

</strong>

やや強気

<br><br>

<strong>

40〜59点

</strong>

中立

<br><br>

<strong>

0〜39点

</strong>

慎重な運用

</div>

</div>


<div class="card">

<h2>

📊 今日の市場データ

</h2>

<table>

<tr>

<td>QQQ</td>

<td style="color:{qqq_color};font-weight:bold;">

{data["change"]:+.2f}%

</td>

</tr>

<tr>

<td>S&P500</td>

<td style="color:{spy_color};font-weight:bold;">

{data["spy_change"]:+.2f}%

</td>

</tr>

<tr>

<td>VIX</td>

<td>

{data["vix"]:.2f}

</td>

</tr>

</table>

</div>

<div class="card">

<h2>

🧠 AI分析

</h2>

<ul>

{reason_html}

</ul>

</div>

<div class="card">

<h2>

🏆 おすすめランキング

</h2>

{ranking_html}

</div>

<footer>

<hr style="border:1px solid #243447;">

<p>

📈 Powered by <strong>PayPay AI</strong>

</p>

<p>

Version 1.1

</p>

<p>

更新日時：{now}

</p>

<p style="font-size:14px;color:#94a3b8;">

このサイトはAIが毎朝マーケットを分析し、
PayPayポイント運用の参考情報を提供しています。

</p>

</footer>

</div>

</body>

</html>
"""

    Path("index.html").write_text(
        html,
        encoding="utf-8"
    )

    print("🌐 Webページ更新")