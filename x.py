from pathlib import Path

def create_post(data, ranking, stats, market_score):

    stars = "★★★★★"

    return f"""📈 PayPay AI

{stars}

🥇 {ranking[0][0]}

QQQ {data['change']:+.2f}%
VIX {data['vix']:.2f}

AI勝率 {stats['win_rate']}%

👇詳細
https://hayato861.github.io/paypay_ai/

#PayPay運用
#投資"""