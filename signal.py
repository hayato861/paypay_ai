def judge(data):

    score = 0
    reasons = []

    if data["ma25"] > data["ma75"]:
        score += 2
        reasons.append("25日線が75日線を上回っています")

    if data["price"] > data["ma25"]:
        score += 1
        reasons.append("価格は25日線より上です")

    if data["vix"] < 20:
        score += 1
        reasons.append("VIXが20以下です")

    stars = "★" * min(score + 1, 5) + "☆" * (5 - min(score + 1, 5))

    if score >= 4:
        action = "PayPayポイントを追加"
    elif score >= 2:
        action = "保有を継続"
    else:
        action = "様子見"

    return stars, reasons, action