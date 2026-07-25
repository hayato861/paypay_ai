import csv
from pathlib import Path


def get_stats():

    file = Path("data/history.csv")

    if not file.exists():
        return {
            "total": 0,
            "win": 0,
            "lose": 0,
            "pending": 0,
            "win_rate": 0
        }

    total = 0
    win = 0
    lose = 0
    pending = 0

    with open(file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            total += 1

            result = row["result"]

            if result == "Win":
                win += 1

            elif result == "Lose":
                lose += 1

            else:
                pending += 1

    finished = win + lose

    if finished == 0:
        rate = 0
    else:
        rate = round(win / finished * 100, 1)

    return {
        "total": total,
        "win": win,
        "lose": lose,
        "pending": pending,
        "win_rate": rate
    }