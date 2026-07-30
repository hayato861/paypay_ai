import csv
from pathlib import Path

file = Path("data/history.csv")

if not file.exists():
    print("history.csvがありません")
    exit()

rows = {}

with open(file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows[row["date"]] = row

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

    for row in rows.values():
        writer.writerow(row)

print("履歴整理完了")