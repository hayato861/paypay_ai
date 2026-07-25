import csv
from pathlib import Path
from datetime import datetime, timedelta


def grade():

    file = Path("data/history.csv")

    if not file.exists():
        return

    rows = []

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            if row["date"] == yesterday and row["result"] == "Pending":

                # ここは後で市場データから判定する
                row["qqq_change"] = "1.20"
                row["result"] = "Win"

            rows.append(row)

    with open(file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "score",
                "recommend",
                "qqq_change",
                "result"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)