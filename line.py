def create_line_message(
    data,
    market_score,
    ranking,
    insight,
    stats
):

    color = "#22c55e"

    if market_score < 40:
        color = "#ef4444"
    elif market_score < 70:
        color = "#f59e0b"

    top_course = ranking[0][0]
    top_score = ranking[0][1]

    return {
        "type": "flex",
        "altText": "PayPay AI Morning Report",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [

                    {
                        "type": "text",
                        "text": "📈 PayPay AI",
                        "weight": "bold",
                        "size": "xl"
                    },

                    {
                        "type": "text",
                        "text": f"市場スコア {market_score}点",
                        "size": "lg",
                        "weight": "bold",
                        "color": color
                    },

                    {
                        "type": "separator",
                        "margin": "lg"
                    },

                    {
                        "type": "text",
                        "text": "🥇 今日のおすすめ",
                        "margin": "lg"
                    },

                    {
                        "type": "text",
                        "text": top_course,
                        "weight": "bold"
                    },

                    {
                        "type": "text",
                        "text": f"{top_score}点"
                    },

                    {
                        "type": "separator",
                        "margin": "lg"
                    },

                    {
                        "type": "text",
                        "text": "📊 市場データ",
                        "margin": "lg"
                    },

                    {
                        "type": "text",
                        "text": f"QQQ {data['change']:+.2f}%"
                    },

                    {
                        "type": "text",
                        "text": f"S&P500 {data['spy_change']:+.2f}%"
                    },

                    {
                        "type": "text",
                        "text": f"VIX {data['vix']:.2f}"
                    }

                ]
            }
        }
    }