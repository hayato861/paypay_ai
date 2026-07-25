from pathlib import Path
from stats import get_stats


def create_post(data, ranking, market_score):

    stats = get_stats()

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

    return f"""📈 PayPay AI

{stars}

🥇 今日のおすすめ
{ranking[0][0]}

QQQ {data['change']:+.2f}%
S&P500 {data['spy_change']:+.2f}%
VIX {data['vix']:.2f}

AI勝率 {stats['win_rate']}%

👇詳細
https://hayato861.github.io/paypay_ai/

#PayPay運用
#投資
"""


def post(report):

    Path("logs/x_post.txt").write_text(
        report,
        encoding="utf-8"
    )

    print("X投稿内容を保存しました")