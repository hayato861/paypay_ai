import csv
import os
from datetime import datetime

CSV_FILE = "data/history.csv"


def save_history(data, stars, reasons, action):

    os.makedirs("data", exist_ok=True)

    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "date",
                "price",
                "spy_change",
                "vix",
                "stars",
                "action",
                "reasons"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d"),
            round(data["price"], 2),
            round(data["spy_change"], 2),
            round(data["vix"], 2),
            stars,
            action,
            " | ".join(reasons)
        ])