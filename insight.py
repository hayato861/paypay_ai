from history import (
    yesterday_diff,
    average_score,
    highest_score,
    lowest_score,
    streak_up,
    streak_down,
    streak_high,
    streak_low
)


def create_insight():

    lines = []

    diff = yesterday_diff()

    if diff is not None:

        if diff > 0:
            lines.append(f"📈 昨日より +{diff}点")

        elif diff < 0:
            lines.append(f"📉 昨日より {diff}点")

        else:
            lines.append("➖ 昨日と同じスコア")

    avg = average_score()

    if avg is not None:
        lines.append(f"📊 7日平均 {avg}点")

    lines.append(f"🏆 過去最高 {highest_score()}点")
    lines.append(f"📉 過去最低 {lowest_score()}点")

    up = streak_up()

    if up >= 2:
        lines.append(f"🔥 {up}日連続で改善")

    down = streak_down()

    if down >= 2:
        lines.append(f"⚠️ {down}日連続で悪化")

    if streak_high():
        lines.append("🚀 3日連続 強気相場")

    if streak_low():
        lines.append("🛡️ 3日連続 守備相場")

    return lines

    