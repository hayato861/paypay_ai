from pathlib import Path
from datetime import datetime

from stats import get_stats

from history import recent_history
import json

import requests

def create_page(
    data,
    market_score,
    ranking,
    reasons,
    insight
):

    stats = get_stats()
    
    comment = ""

    if market_score >= 80:
        comment = (
            "📈 市場は非常に強気です。"
            "積極的な投資を検討できる環境です。"
        )

    elif market_score >= 60:
        comment = (
            "😊 市場は比較的安定しています。"
            "通常通り積立を続けながら、押し目があれば追加投資も検討できます。"
        )

    elif market_score >= 40:
        comment = (
            "🤔 市場は方向感がありません。"
            "焦って売買せず、様子を見ながら積立を続ける局面です。"
        )

    else:
        comment = (
            "⚠️ 市場は弱気です。"
            "無理な買い増しは避け、防御的な運用を意識しましょう。"
        )
        
    comment += "<br><br>"

    comment += "今日の市場判断：<br>"

    for r in reasons:
        comment += f"・{r}<br>"
    if market_score >= 80:
        market_text = "🟢 強気相場"
    elif market_score >= 60:
        market_text = "🟢 やや強気"
    elif market_score >= 40:
        market_text = "🟡 中立"
    elif market_score >= 20:
        market_text = "🟠 やや弱気"
    else:
        market_text = "🔴 弱気相場"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    history = recent_history()
    
    delta = 0

    if len(history) >= 2:
        delta = history[-1]["score"] - history[-2]["score"]
        if delta > 0:
            delta_color = "#22c55e"
        elif delta < 0:
            delta_color = "#ef4444"
        else:
            delta_color = "#9ca3af"
    

    labels = json.dumps([x["date"][5:] for x in history])

    scores = json.dumps([x["score"] for x in history])

    recommend_html = ""

    for row in reversed(history[-5:]):
        recommend_html += f"""
    <tr>
    <td>{row['date'][5:]}</td>
    <td>{row['recommend']}</td>
    </tr>
    """

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
    
    recommend_reason = ""

    if top_course == "テクノロジーチャレンジ":
        recommend_reason = "📈 強気相場向き"

    elif top_course == "ゴールド":
        recommend_reason = "🛡 リスク回避"

    elif top_course == "逆チャレンジ":
        recommend_reason = "📉 下落対策"

    elif top_course == "アメリカ長期国債チャレンジ":
        recommend_reason = "💰 金利低下期待"

    qqq_color = "#22c55e" if data["change"] >= 0 else "#ef4444"
    spy_color = "#22c55e" if data["spy_change"] >= 0 else "#ef4444"
    
    gold_color = "#22c55e"

    if data["gold_change"] < 0:
        gold_color = "#ef4444"
        
    usd_color = "#22c55e"

    if data["usdjpy"] < 145:
        usd_color = "#38bdf8"

    if data["usdjpy"] < 140:
        usd_color = "#ef4444"
    
    # 市場スコア色設定
    score_color = "#22c55e"
    if market_score < 80:
        score_color = "#38bdf8"
    if market_score < 60:
        score_color = "#facc15"
    if market_score < 40:
        score_color = "#ef4444"
    
    # Fear&Greed色設定
    fg = data["fear_greed"]

    if fg >= 75:
        fg_color = "#22c55e"
        fg_text = "🟢 Greed"
    elif fg <= 25:
        fg_color = "#ef4444"
        fg_text = "🔴 Fear"
    else:
        fg_color = "#facc15"
        fg_text = "🟡 Neutral"
            
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
                    毎朝 自動更新
                </div>
                
                <div class="small">
                    更新日時：{now}
                </div>
            </div>
    <div class="grid">

        <!-- 市場スコア -->
    <div class="card">

        <div class="small">
            <h2>市場スコア</h2>
        </div>
        <div
        class="score"
        style="color:{score_color};">

        {market_score}
        </div>
        <div class="market">
            {stars}
        </div>
        <p class="small">
            {market_text}
        </p>
        <p class="small" style="color:{delta_color};">
            昨日比 {delta:+}点
        </p>
    </div>

        <!-- 市場スコア推移 -->
        <div class="card">
            <h2>📈 市場スコア推移</h2>
            <div class="chart-area">
                <canvas id="scoreChart"></canvas>
            </div>
        </div>

        <!-- AI実績 -->
        <div class="card">
            <div class="small">
                <h2>AI実績</h2>
            </div>
<div class="stats-grid">

    <div class="stat-box">
        <div class="stat-title">勝率</div>
        <div class="stat-value">{stats["win_rate"]}%</div>
    </div>

    <div class="stat-box">
        <div class="stat-title">予想</div>
        <div class="stat-value">{stats["total"]}</div>
    </div>

    <div class="stat-box">
        <div class="stat-title">勝ち</div>
        <div class="stat-value">{stats["win"]}</div>
    </div>

    <div class="stat-box">
        <div class="stat-title">負け</div>
        <div class="stat-value">{stats["lose"]}</div>
    </div>

</div>
        </div>
    </div>

    <div class="grid">
        <!-- 今日のおすすめ -->
        <div class="card">
            <div class="small">
                今日のおすすめ
            </div>
            <h2>
                &nbsp;🥇 {top_course}
            </h2>
            <div class="score-mini">
                &nbsp;{top_score}点
            </div>
            <p class="small">
               &nbsp; {recommend_reason}
            </p>
        </div>

        <div class="card">
            <h2>📝 AIコメント</h2>
            <p>
                {comment}
            </p>
        </div>

        <div class="card">
            <h2>🕒 最近のおすすめ</h2>
            <table>
                {recommend_html}
            </table>
        </div>
    </div>


    <div class="grid2">
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
                
                <tr>
                    <td>Fear & Greed</td>
                    <td style="color:{fg_color}">
                        {data["fear_greed"]}
                    </td>
                </tr>

                <tr>
                    <td>ドル円</td>
                    <td>{data["usdjpy"]:.2f}</td>
                </tr>

                <tr>
                    <td>米10年金利</td>
                    <td>{data["tnx"]:.2f}%</td>
                </tr>

                <tr>
                    <td>ゴールド</td>
                    <td style="color:{gold_color}">
                        {data["gold_change"]:+.2f}%
                    </td>

                </tr>
            </table>
        </div>

        <div class="card">
            <h2>🧠 AIインサイト</h2>
            <ul>
                {insight_html}
            </ul>
        </div>
    </div>

    <div class="grid-center">
        <div class="card">
            <h2>🏆 おすすめランキング</h2>
            <table>
                {ranking_html}
            </table>
        </div>
        
        <div class="card">
            <h2>📈 市場スコアとは？</h2>
            <p>
                <strong>市場スコア</strong>は、
                PayPay AIが毎朝マーケットを分析して<br>
                算出する<strong>100点満点の独自評価</strong>です。
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

                ※ QQQ・S&P500・VIX・Fear & Greed指数などを<br>
                もとにAIが毎朝判定しています。

            </p>

        </div>

    </div>

        <footer>
            Powered by PayPay AI
        </footer>

    </div>

    </body>
    
    
    <script>
        const scoreLabels = {labels};
        const scoreData = {scores};
    </script>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="js/chart.js"></script>

</html>
"""

    output = Path("index.html")

    output.write_text(
        html,
        encoding="utf-8"
    )

    print("保存先:", output.resolve())
    
def get_fear_greed():

    try:

        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        r.raise_for_status()

        data = r.json()

        return int(data["fear_and_greed"]["score"])

    except Exception as e:

        print("Fear&Greed取得失敗", e)

        return 50