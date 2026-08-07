def score_market(data):
    
    score = 50

    reasons = []

    fg = data["fear_greed"]

    if fg >= 80:
        score += 15
        reasons.append("Fear & Greedは極めて強気です")

    elif fg >= 60:
        score += 8
        reasons.append("Fear & Greedは強気です")

    elif fg <= 20:
        score -= 15
        reasons.append("Fear & Greedは極度の恐怖です")

    elif fg <= 40:
        score -= 8
        reasons.append("Fear & Greedは弱気です")

    # QQQ
    if data["change"] > 2:
        score += 20
        reasons.append("QQQが大きく上昇しています")

    elif data["change"] > 0:
        score += 5
        reasons.append("QQQは上昇しています")

    elif data["change"] < -2:
        score -= 20
        reasons.append("QQQが大きく下落しています")

    elif data["change"] < 0:
        score -= 5
        reasons.append("QQQは下落しています")

    # S&P500
    if data["spy_change"] > 0:
        score += 5
        reasons.append("S&P500が上昇しています")

    elif data["spy_change"] < 0:
        score -= 5
        reasons.append("S&P500が下落しています")

    # VIX
    if data["vix"] < 16:
        score += 10
        reasons.append("VIXが非常に低く市場心理は良好です")

    elif data["vix"] < 20:
        score += 5
        reasons.append("VIXは落ち着いています")

    elif data["vix"] > 30:
        score -= 25
        reasons.append("VIXが急上昇し警戒が必要です")

    elif data["vix"] > 25:
        score -= 15
        reasons.append("VIXが高く注意が必要です")

    score = max(0, min(score, 100))
        # 何も理由がない場合
    if not reasons:
        if score >= 70:
            reasons.append("市場は強気です。")

        elif score >= 40:
            reasons.append("市場は中立です。")

        else:
            reasons.append("市場は慎重相場です。")
            
    # Gold
    if data["gold_change"] > 1:
        score -= 5
        reasons.append("金価格が上昇しています")

    # 米金利
    if data["tnx_change"] > 1:
        score -= 5
        reasons.append("長期金利が上昇しています")

    # ドル円
    if data["usdjpy_change"] > 1:
        score += 3
        reasons.append("ドル円は円安です")    
        
    return score, reasons


def recommend_courses(data, market_score):

    fg = data["fear_greed"]    
    if fg >= 75:
        courses["テクノロジーチャレンジ"] += 5
        courses["テクノロジー"] += 5
    elif fg <= 25:
        courses["ゴールド"] += 5
        courses["逆チャレンジ"] += 5
    
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
    for course in courses:
        courses[course] = min(courses[course], 100)
    ranking = sorted(
        courses.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return ranking