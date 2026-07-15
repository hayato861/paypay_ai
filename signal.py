def score_market(data):
    
    score = 50
    reasons = []

    # QQQ
    if data["change"] > 1:
        score += 15
        reasons.append("QQQが1%以上上昇しています")

    elif data["change"] < -1:
        score -= 15
        reasons.append("QQQが1%以上下落しています")

    # S&P500
    if data["spy_change"] > 0.5:
        score += 10
        reasons.append("S&P500が堅調です")

    elif data["spy_change"] < -0.5:
        score -= 10
        reasons.append("S&P500が弱い動きです")

    # VIX
    if data["vix"] < 18:
        score += 10
        reasons.append("VIXが低く市場心理は良好です")

    elif data["vix"] > 25:
        score -= 20
        reasons.append("VIXが高く警戒が必要です")

    score = max(0, min(score, 100))

    return score, reasons


def recommend_courses(data, market_score):
    
    courses = {
        "テクノロジーチャレンジ": 80,
        "テクノロジー": 80,
        "チャレンジ": 80,
        "スタンダード": 80,
        "ゴールド": 80,
        "アメリカ長期国債チャレンジ": 80,
        "逆チャレンジ": 80,
    }

    # 市場スコア
    if market_score >= 80:
        courses["テクノロジーチャレンジ"] += 10
        courses["テクノロジー"] += 8
        courses["チャレンジ"] += 5

    elif market_score <= 40:
        courses["ゴールド"] += 12
        courses["アメリカ長期国債チャレンジ"] += 10
        courses["逆チャレンジ"] += 8

    # NASDAQ(QQQ)
    if data["change"] > 1:
        courses["テクノロジーチャレンジ"] += 8
        courses["テクノロジー"] += 6

    elif data["change"] < -1:
        courses["逆チャレンジ"] += 8

    # S&P500
    if data["spy_change"] > 0:
        courses["スタンダード"] += 5
        courses["チャレンジ"] += 3

    # VIX
    if data["vix"] < 18:
        courses["テクノロジーチャレンジ"] += 5

    elif data["vix"] > 25:
        courses["ゴールド"] += 10
        courses["アメリカ長期国債チャレンジ"] += 8

    ranking = sorted(
        courses.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranking