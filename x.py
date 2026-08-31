from pathlib import Path
from math import isfinite

from stats import get_stats


def create_x_post(data, market_score, ranking, insight):
    for key in ("change", "spy_change", "vix"):
        if not isfinite(float(data[key])):
            raise ValueError(f"X原稿に使用できない市場データです: {key}")

    top_course, top_score = ranking[0]

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

    stats = get_stats()
    win_rate = "—" if stats["win_rate"] is None else f'{stats["win_rate"]}%'

    return f"""📈 PayPay AI
市場 {market_score}/100 {market_text}
🥇 {top_course} {top_score}点

QQQ {data["change"]:+.2f}% / S&P500 {data["spy_change"]:+.2f}%
VIX {data["vix"]:.2f}
実ETF勝率 {win_rate}（{stats['verified_total']}件）

#PayPayポイント運用"""


def save_x_draft(text, image_path=None, output=Path("data/x_post.txt")):
    output = Path(output)
    output.parent.mkdir(exist_ok=True)
    output.write_text(text.rstrip() + "\n", encoding="utf-8")

    print("X手動投稿用テキストを保存:", output)

    if image_path:
        print("X手動添付画像:", image_path)
    else:
        print("X手動添付画像なし")

    return output


def post(report, image_path=None):
    """旧呼び出しとの互換用。X APIへの送信は行わない。"""
    return save_x_draft(report, image_path)
