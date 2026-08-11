def create_ai_signal(market_score, ml_probability):
    """
    市場スコアとML予測確率を統合して
    AI総合判定を作る
    """

    # --------------------------------------------------
    # 1. ML確率を0〜100に変換
    # --------------------------------------------------

    ml_score = ml_probability * 100

    # --------------------------------------------------
    # 2. 総合スコア
    #
    # 市場スコア 60%
    # ML予測     40%
    # --------------------------------------------------

    ai_score = (
        market_score * 0.6
        + ml_score * 0.4
    )

    ai_score = round(ai_score, 1)

    # --------------------------------------------------
    # 3. 判定
    # --------------------------------------------------

    if ai_score >= 70:

        judgment = "強気"

    elif ai_score >= 60:

        judgment = "やや強気"

    elif ai_score >= 45:

        judgment = "様子見"

    elif ai_score >= 30:

        judgment = "やや弱気"

    else:

        judgment = "弱気"

    # --------------------------------------------------
    # 4. ML信頼度
    # --------------------------------------------------

    distance = abs(ml_probability - 0.5)

    if distance >= 0.20:

        confidence = "高"

    elif distance >= 0.10:

        confidence = "中"

    else:

        confidence = "低"

    return {
        "market_score": market_score,
        "ml_probability": round(
            ml_probability * 100,
            1
        ),
        "ai_score": ai_score,
        "judgment": judgment,
        "confidence": confidence,
    }