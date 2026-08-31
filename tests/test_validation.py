import unittest
import csv
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from backtest import evaluate_next_day, load_market_history
from grader import grade
from validation import (
    directional_accuracy,
    evaluate_predictions,
    majority_baseline,
    passes_adoption_gate,
    recommendation_prediction,
)


class ValidationTest(unittest.TestCase):
    def test_directional_accuracy(self):
        self.assertEqual(directional_accuracy([1, 0, 1], [1, 1, 1]), 2 / 3)

    def test_majority_baseline(self):
        self.assertEqual(majority_baseline([1, 1, 1, 0]), 0.75)

    def test_recommendation_direction(self):
        predictions = recommendation_prediction([
            "テクノロジー",
            "ゴールド",
            "逆チャレンジ",
            "スタンダード",
        ])
        self.assertEqual(predictions.tolist(), [1, 0, 0, 1])

    def test_edge_is_measured_against_majority_baseline(self):
        result = evaluate_predictions([1, 1, 1, 0], [1, 1, 0, 0])
        self.assertEqual(result["accuracy"], 0.75)
        self.assertEqual(result["baseline"], 0.75)
        self.assertEqual(result["edge"], 0.0)

    def test_adoption_gate_requires_samples_and_positive_edge(self):
        self.assertTrue(passes_adoption_gate({"samples": 200, "edge": 0.02}))
        self.assertFalse(passes_adoption_gate({"samples": 199, "edge": 0.10}))
        self.assertFalse(passes_adoption_gate({"samples": 500, "edge": 0.019}))

    @patch("backtest.yf.Ticker")
    def test_market_history_is_anchored_to_qqq_trading_days(self, ticker):
        indexes = {
            "QQQ": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "SPY": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "^VIX": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "GLD": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "^TNX": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "JPY=X": pd.to_datetime([
                "2026-01-02",
                "2026-01-03",
                "2026-01-05",
            ]),
            "TQQQ": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "SQQQ": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "SPXL": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "SPXS": pd.to_datetime(["2026-01-02", "2026-01-05"]),
            "TMF": pd.to_datetime(["2026-01-02", "2026-01-05"]),
        }

        def history_for(symbol):
            index = indexes[symbol]
            return pd.DataFrame({"Close": range(100, 100 + len(index))}, index=index)

        ticker.side_effect = lambda symbol: type(
            "FakeTicker",
            (),
            {"history": lambda self, **kwargs: history_for(symbol)},
        )()

        result = load_market_history("5d")

        self.assertEqual(
            result.index.tolist(),
            indexes["QQQ"].tolist(),
        )

    def test_next_day_uses_recommended_course_etf(self):
        today = pd.Series({"QQQ": 100.0, "TQQQ": 100.0})
        tomorrow = pd.Series({"QQQ": 99.0, "TQQQ": 103.0})

        change, result = evaluate_next_day(
            today,
            tomorrow,
            "テクノロジーチャレンジ",
        )

        self.assertAlmostEqual(change, 3.0)
        self.assertEqual(result, "Win")

    @patch("grader.load_course_returns")
    def test_grader_uses_real_course_return_and_keeps_future_pending(self, load):
        load.side_effect = lambda ticker, start, end: pd.Series(
            [3.0 if ticker == "TQQQ" else -2.0],
            index=pd.to_datetime(["2026-08-28"]),
        )

        with tempfile.TemporaryDirectory() as directory:
            history = Path(directory) / "history.csv"
            with history.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=["date", "score", "recommend", "qqq_change", "result"],
                )
                writer.writeheader()
                writer.writerows([
                    {
                        "date": "2026-08-28",
                        "score": "70",
                        "recommend": "テクノロジーチャレンジ",
                        "qqq_change": "",
                        "result": "Pending",
                    },
                    {
                        "date": "2026-08-30",
                        "score": "60",
                        "recommend": "逆チャレンジ",
                        "qqq_change": "",
                        "result": "Pending",
                    },
                ])

            grade(today=date(2026, 8, 31), file=history)

            with history.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))

        self.assertEqual(rows[0]["qqq_change"], "3.00")
        self.assertEqual(rows[0]["result"], "Win")
        self.assertEqual(rows[1]["qqq_change"], "")
        self.assertEqual(rows[1]["result"], "Pending")


if __name__ == "__main__":
    unittest.main()
