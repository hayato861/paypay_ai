import unittest
import csv
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from backtest import evaluate_next_day, load_market_history
from grader import grade
from market import clean_history
from stats import get_stats
from notify import notify
from publisher import publish
from x import create_x_post, save_x_draft
from commercial_readiness import Check, report
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

    def test_stats_excludes_legacy_results_from_verified_rate(self):
        with tempfile.TemporaryDirectory() as directory:
            history = Path(directory) / "history.csv"
            with history.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=[
                        "date",
                        "score",
                        "recommend",
                        "qqq_change",
                        "result",
                        "evaluation_source",
                    ],
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerows([
                    {
                        "date": "2026-08-26",
                        "score": "50",
                        "recommend": "テクノロジー",
                        "qqq_change": "1.20",
                        "result": "Win",
                        "evaluation_source": "legacy",
                    },
                    {
                        "date": "2026-08-27",
                        "score": "70",
                        "recommend": "テクノロジー",
                        "qqq_change": "0.50",
                        "result": "Win",
                        "evaluation_source": "etf_v1",
                    },
                    {
                        "date": "2026-08-28",
                        "score": "60",
                        "recommend": "テクノロジー",
                        "qqq_change": "-0.50",
                        "result": "Lose",
                        "evaluation_source": "etf_v1",
                    },
                    {
                        "date": "2026-08-29",
                        "score": "60",
                        "recommend": "テクノロジー",
                        "qqq_change": "",
                        "result": "Pending",
                        "evaluation_source": "",
                    },
                ])

            stats = get_stats(history)

        self.assertEqual(stats["verified_total"], 2)
        self.assertEqual(stats["win_rate"], 50.0)
        self.assertEqual(stats["legacy"], 1)
        self.assertEqual(stats["pending"], 1)

    @patch("notify.requests.post")
    @patch("notify.LINE_CHANNEL_ACCESS_TOKEN", "test-token")
    def test_line_notification_checks_http_result(self, post):
        response = Mock(status_code=200)
        post.return_value = response

        result = notify("test message")

        self.assertIs(result, response)
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(post.call_args.kwargs["timeout"], 15)
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"],
            "Bearer test-token",
        )

    @patch("notify.LINE_CHANNEL_ACCESS_TOKEN", None)
    def test_line_notification_requires_token(self):
        with self.assertRaises(RuntimeError):
            notify("test message")

    @patch("x.get_stats")
    def test_x_draft_is_short_and_saved_for_manual_post(self, stats):
        stats.return_value = {"win_rate": 50.0, "verified_total": 2}
        text = create_x_post(
            {"change": 0.5, "spy_change": 0.3, "vix": 15.2},
            60,
            [("テクノロジーチャレンジ", 85)],
            [],
        )

        self.assertLessEqual(len(text), 280)
        self.assertIn("実ETF勝率 50.0%（2件）", text)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "x_post.txt"
            save_x_draft(text, "data/market_report.png", output)
            saved = output.read_text(encoding="utf-8")

        self.assertEqual(saved, text + "\n")

    def test_market_history_ignores_trailing_nan_close(self):
        history = pd.DataFrame(
            {"Close": [100.0, 101.0, float("nan")]},
            index=pd.to_datetime(["2026-08-27", "2026-08-28", "2026-08-31"]),
        )

        cleaned = clean_history(history, "QQQ")

        self.assertEqual(cleaned["Close"].tolist(), [100.0, 101.0])

    @patch("x.get_stats")
    def test_x_draft_rejects_nan_market_data(self, stats):
        stats.return_value = {"win_rate": None, "verified_total": 0}

        with self.assertRaises(ValueError):
            create_x_post(
                {"change": float("nan"), "spy_change": 0.3, "vix": 15.2},
                60,
                [("テクノロジー", 80)],
                [],
            )

    @patch("publisher.save_x_draft")
    @patch("publisher.create_x_post", return_value="x draft")
    @patch("publisher.create_market_image", return_value=Path("data/market_report.png"))
    @patch("publisher.notify")
    @patch("publisher.create_page")
    @patch("publisher.log")
    def test_publish_sends_line_but_only_saves_x_draft(
        self,
        log,
        create_page,
        line_notify,
        create_image,
        create_post,
        save_draft,
    ):
        data = {"change": 0.5, "spy_change": 0.3, "vix": 15.2}
        ranking = [("テクノロジーチャレンジ", 85)]

        publish("line report", data, 60, ranking, [], [])

        line_notify.assert_called_once_with("line report")
        create_image.assert_called_once()
        create_post.assert_called_once_with(data, 60, ranking, [])
        save_draft.assert_called_once_with(
            "x draft",
            Path("data/market_report.png"),
        )

    def test_paid_launch_requires_every_readiness_check(self):
        blocked = report([
            Check("legal", True, "ok"),
            Check("model", False, "below baseline"),
        ])
        ready = report([
            Check("legal", True, "ok"),
            Check("model", True, "ok"),
        ])

        self.assertFalse(blocked["ready_for_paid_launch"])
        self.assertTrue(ready["ready_for_paid_launch"])


if __name__ == "__main__":
    unittest.main()
