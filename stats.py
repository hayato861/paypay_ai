import csv
from pathlib import Path


def get_stats(file=Path("data/history.csv")):

    file = Path(file)

    if not file.exists():
        return empty_stats()

    total = 0
    verified_win = 0
    verified_lose = 0
    pending = 0
    legacy = 0

    with open(file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            total += 1

            result = row.get("result", "Pending")
            source = row.get("evaluation_source", "")

            if source == "etf_v1" and result == "Win":
                verified_win += 1

            elif source == "etf_v1" and result == "Lose":
                verified_lose += 1

            elif result in {"Win", "Lose"}:
                legacy += 1

            else:
                pending += 1

    verified_total = verified_win + verified_lose

    if verified_total == 0:
        rate = None
    else:
        rate = round(verified_win / verified_total * 100, 1)

    return {
        "total": total,
        "verified_total": verified_total,
        "win": verified_win,
        "lose": verified_lose,
        "pending": pending,
        "legacy": legacy,
        "win_rate": rate,
    }


def empty_stats():
    return {
        "total": 0,
        "verified_total": 0,
        "win": 0,
        "lose": 0,
        "pending": 0,
        "legacy": 0,
        "win_rate": None,
    }
