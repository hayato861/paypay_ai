import csv
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from courses import COURSE_TICKERS
from history import HISTORY_FIELDS, ensure_history_schema
from clock import now_jst


def load_course_returns(ticker, start_date, end_date):
    try:
        history = yf.Ticker(ticker).history(
            start=start_date - timedelta(days=7),
            end=end_date + timedelta(days=1),
            interval="1d",
            auto_adjust=False,
        )
    except Exception as error:
        print(f"採点データ取得失敗 ({ticker}): {error}")
        return pd.Series(dtype=float)

    if history.empty:
        return pd.Series(dtype=float)

    index = pd.to_datetime(history.index)
    if index.tz is not None:
        index = index.tz_localize(None)

    close = pd.Series(history["Close"].to_numpy(), index=index.normalize())
    return close.pct_change() * 100


def grade(today=None, file=Path("data/history.csv")):

    file = Path(file)

    if not file.exists():
        return

    ensure_history_schema(file)

    rows = []
    today = today or now_jst().date()

    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        rows = list(reader)

    pending = [
        row for row in rows
        if row.get("result") == "Pending"
        and row.get("recommend") in COURSE_TICKERS
        and date.fromisoformat(row["date"]) < today
    ]

    if pending:
        start_date = min(date.fromisoformat(row["date"]) for row in pending)
        returns_by_ticker = {
            ticker: load_course_returns(ticker, start_date, today)
            for ticker in {COURSE_TICKERS[row["recommend"]] for row in pending}
        }

        for row in pending:
            prediction_date = pd.Timestamp(row["date"])
            ticker = COURSE_TICKERS[row["recommend"]]
            available = returns_by_ticker[ticker]
            available = available[
                (available.index >= prediction_date)
                & (available.index < pd.Timestamp(today))
            ].dropna()

            if available.empty:
                continue

            change = float(available.iloc[0])
            # CSV列名は既存データとの互換性のため維持するが、
            # 保存値は推薦コース連動ETFの実リターン。
            row["qqq_change"] = f"{change:.2f}"
            row["result"] = "Win" if change > 0 else "Lose"
            row["evaluation_source"] = "etf_v1"

    with open(file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=HISTORY_FIELDS,
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)
