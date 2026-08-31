import unittest
import csv
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from backtest import evaluate_next_day, load_market_history
from grader import grade
from market import clean_history
from stats import get_stats
from notify import notify, notify_paid_member
from publisher import publish, publish_premium
from report import create_premium_report
from x import create_x_post, save_x_draft
from commercial_readiness import Check, report
from clock import JST
from service import adsense_html, premium_preview_html
from service import write_ads_txt
from premium_web import create_premium_page
from premium_report_web import create_premium_report_page
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

    @patch("notify.requests.post")
    @patch("notify.LINE_CHANNEL_ACCESS_TOKEN", "test-token")
    def test_paid_line_notification_uses_individual_push_and_retry_key(self, post):
        response = Mock(status_code=200)
        post.return_value = response

        notify_paid_member("premium report", "U123", "retry-key")

        self.assertEqual(post.call_args.args[0], "https://api.line.me/v2/bot/message/push")
        self.assertEqual(post.call_args.kwargs["json"]["to"], "U123")
        self.assertEqual(
            post.call_args.kwargs["headers"]["X-Line-Retry-Key"],
            "retry-key",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_ads_are_disabled_by_default(self):
        self.assertEqual(adsense_html(), "")

    @patch.dict(
        "os.environ",
        {
            "ADS_ENABLED": "true",
            "ADS_CONSENT_READY": "true",
            "ADSENSE_CLIENT": "ca-pub-test",
            "ADSENSE_SLOT": "12345",
            "PRIVACY_URL": "https://example.com/privacy?a=1&b=2",
        },
        clear=True,
    )
    def test_ads_require_explicit_configuration(self):
        html = adsense_html()
        self.assertIn('data-ad-client="ca-pub-test"', html)
        self.assertIn('data-ad-slot="12345"', html)
        self.assertIn("privacy?a=1&amp;b=2", html)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ads.txt"
            self.assertEqual(write_ads_txt(output), output)
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                "google.com, pub-test, DIRECT, f08c47fec0942fa0\n",
            )

    @patch.dict("os.environ", {"PREMIUM_SIGNUP_URL": "https://example.com/waitlist?a=1&b=2"})
    def test_premium_signup_url_is_escaped(self):
        self.assertIn("a=1&amp;b=2", premium_preview_html())

    @patch.dict(
        "os.environ",
        {
            "PAID_LAUNCH_ENABLED": "true",
            "LEGAL_REVIEW_APPROVED": "false",
            "STRIPE_CHECKOUT_URL": "https://checkout.example/session",
        },
        clear=True,
    )
    def test_premium_page_does_not_sell_before_legal_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "premium.html"
            create_premium_page(output)
            html = output.read_text(encoding="utf-8")
        self.assertIn("準備中・課金未開始", html)
        self.assertNotIn("checkout.example", html)
        self.assertIn("<span>数字だけで終わらない。</span>", html)
        self.assertIn("変化点と背景", html)
        self.assertIn("リスク監視", html)
        self.assertIn("よくある質問", html)

    @patch.dict("os.environ", {"MEMBER_APP_URL": "https://members.example.com/"}, clear=True)
    def test_premium_page_links_to_separate_member_app(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "premium.html"
            create_premium_page(output)
            html = output.read_text(encoding="utf-8")
        self.assertIn('href="https://members.example.com/login"', html)

    @patch("premium_report_web.now_jst", return_value=datetime(2026, 8, 31, 10, 0, tzinfo=JST))
    @patch("premium_report_web.yesterday_diff", return_value=5)
    @patch("premium_report_web.average_score", return_value=62.5)
    def test_private_premium_html_contains_member_analysis(self, average, delta, now):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "private" / "premium_report.html"
            create_premium_report_page(
                {"change": -2.5, "spy_change": -1.2, "vix": 30.0},
                55,
                [("ゴールド", 80), ("テクノロジー", 65)],
                ["金利上昇"],
                ["警戒感が上昇"],
                output,
            )
            html = output.read_text(encoding="utf-8")
        self.assertIn("2026-08-31 10:00 JST", html)
        self.assertIn("前日比", html)
        self.assertIn("VIX 30.00", html)
        self.assertIn('content="noindex,nofollow,noarchive"', html)

    def test_jst_timezone_has_expected_offset(self):
        value = datetime(2026, 8, 31, 10, 0, tzinfo=JST)
        self.assertEqual(value.utcoffset().total_seconds(), 9 * 60 * 60)

    @patch("report.yesterday_diff", return_value=5)
    @patch("report.average_score", return_value=62.5)
    def test_premium_report_contains_trend_and_risk_analysis(self, average, delta):
        text = create_premium_report(
            {"vix": 30.0, "change": -2.5},
            55,
            ["金利上昇"],
            [("ゴールド", 80)],
            ["警戒感が上昇"],
        )

        self.assertIn("前日比 +5点", text)
        self.assertIn("7日平均：62.5点", text)
        self.assertIn("VIXが30.00", text)
        self.assertIn("将来の成果を保証しません", text)

    @patch("publisher.notify_paid_member")
    def test_premium_publisher_uses_validated_individual_delivery(self, send):
        publish_premium("report", "U123", "retry-key")
        send.assert_called_once_with("report", "U123", "retry-key")

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
    @patch("publisher.create_premium_report_page")
    @patch("publisher.create_premium_page")
    @patch("publisher.create_page")
    @patch("publisher.log")
    def test_publish_sends_line_but_only_saves_x_draft(
        self,
        log,
        create_page,
        create_premium,
        create_premium_report_html,
        line_notify,
        create_image,
        create_post,
        save_draft,
    ):
        data = {"change": 0.5, "spy_change": 0.3, "vix": 15.2}
        ranking = [("テクノロジーチャレンジ", 85)]

        publish("line report", data, 60, ranking, [], [])

        line_notify.assert_called_once_with("line report")
        create_premium.assert_called_once_with()
        create_premium_report_html.assert_called_once_with(
            data, 60, ranking, [], []
        )
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
