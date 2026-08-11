from pathlib import Path
from stats import get_stats


def create_x_post(data, market_score, ranking, insight):

    top_course = ranking[0][0]
    top_score = ranking[0][1]

    # 市場判定
    if market_score >= 80:
        market_text = "★★★★★ 強気"

    elif market_score >= 60:
        market_text = "★★★★☆ やや強気"

    elif market_score >= 40:
        market_text = "★★★☆☆ 中立"

    elif market_score >= 20:
        market_text = "★★☆☆☆ やや弱気"

    else:
        market_text = "★☆☆☆☆ 弱気"


    # AIインサイト
    insight_text = ""

    for item in insight[:4]:
        insight_text += f"・{item}\n"


    text = f"""📈 PayPay AI Morning Report

市場スコア：{market_score} / 100
{market_text}

🥇 今日のおすすめ
{top_course}
{top_score}点

📊 市場
QQQ {data["change"]:+.2f}%
S&P500 {data["spy_change"]:+.2f}%
VIX {data["vix"]:.2f}

🧠 AIインサイト
{insight_text}

毎朝自動更新しています。
"""

    return text


def post(report, image_path=None):

    # X投稿内容を保存
    output = Path("logs/x_post.txt")

    output.parent.mkdir(
        exist_ok=True
    )

    output.write_text(
        report,
        encoding="utf-8"
    )

    print("X投稿内容を保存しました")

    # 画像が生成されている場合
    if image_path:

        print("X投稿画像:", image_path)

    else:

        print("X投稿画像なし")