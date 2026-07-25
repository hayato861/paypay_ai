import csv
from pathlib import Path
from datetime import datetime


def save_history(score, recommend):

    Path("data").mkdir(exist_ok=True)

    file = Path("data/history.csv")

    exists = file.exists()

    with open(file, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        if not exists:
            writer.writerow([
                "date",
                "score",
                "recommend",
                "qqq_change",
                "result"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"),
            score,
            recommend,
            "",
            "Pending"
        ])