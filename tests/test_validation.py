import unittest
from unittest.mock import patch

import pandas as pd

from backtest import load_market_history
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


if __name__ == "__main__":
    unittest.main()
