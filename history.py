import csv
from pathlib import Path
from datetime import datetime

HISTORY_FIELDS = [
    "date",
    "score",
    "recommend",
    "qqq_change",
    "result",
    "evaluation_source",
]


def ensure_history_schema(file=Path("data/history.csv")):
    file = Path(file)

    if not file.exists():
        return

    with file.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if fieldnames == HISTORY_FIELDS:
        return

    for row in rows:
        if "evaluation_source" not in row:
            row["evaluation_source"] = (
                "legacy" if row.get("result") in {"Win", "Lose"} else ""
            )

    with file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=HISTORY_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in HISTORY_FIELDS} for row in rows)


def save_history(score, recommend):

    Path("data").mkdir(exist_ok=True)
    file = Path("data/history.csv")
    today = datetime.now().strftime("%Y-%m-%d")
    ensure_history_schema(file)

    if file.exists():

        with open(file, newline="", encoding="utf-8") as f:

            reader = csv.DictReader(f)

            for row in reader:

                if row["date"] == today:
                    print("今日の履歴は保存済み")
                    return

    exists = file.exists()

    with open(file, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f, lineterminator="\n")

        if not exists:
            writer.writerow(HISTORY_FIELDS)

        writer.writerow([
            today,
            score,
            recommend,
            "",
            "Pending",
            "",
        ])
        
        
def load_history():

    file = Path("data/history.csv")

    if not file.exists():
        return []

    ensure_history_schema(file)

    rows = []

    with open(file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            score = row.get("score", "").strip()

            if score == "":
                row["score"] = 0
            else:
                row["score"] = int(score)

            rows.append(row)

    return rows

def yesterday_diff():

    history = load_history()

    if len(history) < 2:
        return None

    return history[-1]["score"] - history[-2]["score"]

def average_score(days=7):

    history = load_history()

    if not history:
        return None

    scores = [
        row["score"]
        for row in history[-days:]
    ]

    return round(sum(scores) / len(scores), 1)

def highest_score():

    history = load_history()

    if not history:
        return None

    return max(row["score"] for row in history)

def lowest_score():

    history = load_history()

    if not history:
        return None

    return min(row["score"] for row in history)

def streak_high(days=3):

    history = load_history()

    if len(history) < days:
        return False

    target = history[-days:]

    return all(row["score"] >= 70 for row in target)

def streak_low(days=3):

    history = load_history()

    if len(history) < days:
        return False

    target = history[-days:]

    return all(row["score"] <= 40 for row in target)

def streak_up():

    history = load_history()

    if len(history) < 2:
        return 0

    count = 1

    for i in range(len(history)-1,0,-1):

        if history[i]["score"] > history[i-1]["score"]:
            count += 1
        else:
            break

    return count

def streak_down():

    history = load_history()

    if len(history) < 2:
        return 0

    count = 1

    for i in range(len(history)-1,0,-1):

        if history[i]["score"] < history[i-1]["score"]:
            count += 1
        else:
            break

    return count

def recent_history(days=14):

    history = load_history()

    return history[-days:]
