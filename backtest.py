import yfinance as yf
import pandas as pd
from pathlib import Path
import pandas as pd
import numpy as np
from scoring import score_market, recommend_courses

# ============================================================
# Train / Test 分離
# ============================================================

def train_test_analysis(df):

    print()
    print("=" * 50)
    print("🧪 Train / Test 分析")
    print("=" * 50)

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")

    split_date = pd.Timestamp("2025-01-01")

    train = df[df["date"] < split_date].copy()
    test = df[df["date"] >= split_date].copy()

    print()
    print("📚 TRAIN")
    print("-" * 40)

    print(
        f"{train['date'].min().date()} "
        f"～ "
        f"{train['date'].max().date()}"
    )

    print(f"件数: {len(train)}")

    print()
    print("🧪 TEST")
    print("-" * 40)

    print(
        f"{test['date'].min().date()} "
        f"～ "
        f"{test['date'].max().date()}"
    )

    print(f"件数: {len(test)}")

    # --------------------------------------------------------
    # 勝率
    # --------------------------------------------------------

    train_win_rate = (
        train["result"].eq("Win").mean() * 100
    )

    test_win_rate = (
        test["result"].eq("Win").mean() * 100
    )

    print()
    print("📊 勝率")
    print("-" * 40)

    print(f"TRAIN : {train_win_rate:.1f}%")
    print(f"TEST  : {test_win_rate:.1f}%")

    # --------------------------------------------------------
    # スコア帯
    # --------------------------------------------------------

    thresholds = [40, 50, 60, 70, 80]

    print()
    print("📈 スコア閾値")
    print("-" * 40)

    for threshold in thresholds:

        train_high = train[
            train["score"] >= threshold
        ]

        test_high = test[
            test["score"] >= threshold
        ]

        if len(train_high) > 0:
            train_rate = (
                train_high["result"].eq("Win").mean()
                * 100
            )
        else:
            train_rate = np.nan

        if len(test_high) > 0:
            test_rate = (
                test_high["result"].eq("Win").mean()
                * 100
            )
        else:
            test_rate = np.nan

        print(
            f"Score >= {threshold}: "
            f"TRAIN {train_rate:.1f}% "
            f"({len(train_high)}回) / "
            f"TEST {test_rate:.1f}% "
            f"({len(test_high)}回)"
        )

    # --------------------------------------------------------
    # 相関
    # --------------------------------------------------------

    print()
    print("🔬 スコアと翌日QQQ")
    print("-" * 40)

    train_corr = train["score"].corr(
        train["next_day_qqq"]
    )

    test_corr = test["score"].corr(
        test["next_day_qqq"]
    )

    print(f"TRAIN : {train_corr:+.3f}")
    print(f"TEST  : {test_corr:+.3f}")

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    train.to_csv(
        "data/backtest_train.csv",
        index=False,
        encoding="utf-8-sig"
    )

    test.to_csv(
        "data/backtest_test.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("💾 保存")
    print("  data/backtest_train.csv")
    print("  data/backtest_test.csv")

    return train, test


TICKERS = {
    "QQQ": "QQQ",
    "SPY": "SPY",
    "VIX": "^VIX",
    "GLD": "GLD",
    "TNX": "^TNX",
    "USDJPY": "JPY=X",
}


def load_market_history(period="5y"):
    """
    過去の市場データをまとめて取得する。
    各市場の休場日が異なるため、
    日付を outer join して前回値で補完する。
    """

    print("📥 過去データ取得開始")

    data = {}

    for name, ticker in TICKERS.items():

        print(f"  {name} ...")

        df = yf.Ticker(ticker).history(
            period=period,
            interval="1d",
            auto_adjust=False
        )

        if df.empty:
            raise ValueError(
                f"{name} のデータを取得できませんでした"
            )

        df = df[["Close"]].copy()

        # タイムゾーンを除去
        df.index = pd.to_datetime(df.index)

        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        df.columns = [name]

        data[name] = df

    # ----------------------------------------
    # 全データを日付ベースで結合
    # ----------------------------------------

    merged = None

    for name, df in data.items():

        if merged is None:
            merged = df

        else:
            merged = merged.join(
                df,
                how="outer"
            )

    # ----------------------------------------
    # 日付順に並べる
    # ----------------------------------------

    merged = merged.sort_index()

    # ----------------------------------------
    # 休日などで欠けているデータを
    # 直近の値で補完
    # ----------------------------------------

    merged = merged.ffill()

    # ----------------------------------------
    # それでも先頭に欠損が残っている
    # データは削除
    # ----------------------------------------

    merged = merged.dropna()

    if merged.empty:
        raise ValueError(
            "市場データを結合した結果、"
            "有効なデータが0件になりました。"
        )

    print(
        f"✅ データ取得完了: "
        f"{merged.index[0].date()} ～ "
        f"{merged.index[-1].date()}"
    )

    print(
        f"📊 データ件数: {len(merged)}日"
    )

    return merged


def prepare_indicators(df):
    """
    現在のPayPay AIで使っている指標を計算する。
    """

    df = df.copy()

    # QQQ移動平均
    df["MA25"] = (
        df["QQQ"]
        .rolling(25)
        .mean()
    )

    df["MA75"] = (
        df["QQQ"]
        .rolling(75)
        .mean()
    )

    # 前日比
    df["QQQ_change"] = (
        df["QQQ"]
        .pct_change()
        * 100
    )

    df["SPY_change"] = (
        df["SPY"]
        .pct_change()
        * 100
    )

    df["GLD_change"] = (
        df["GLD"]
        .pct_change()
        * 100
    )

    df["TNX_change"] = (
        df["TNX"]
        .pct_change()
        * 100
    )

    df["USDJPY_change"] = (
        df["USDJPY"]
        .pct_change()
        * 100
    )

    return df


def make_market_data(row):
    """
    現在の score_market() が受け取る
    data形式に変換する。
    """

    return {
        "change": float(row["QQQ_change"]),
        "spy_change": float(row["SPY_change"]),
        "vix": float(row["VIX"]),

        "ma25": float(row["MA25"]),
        "ma75": float(row["MA75"]),

        # 過去Fear & Greedはまだ再現しない
        "fear_greed": 50,

        "gold_change": float(row["GLD_change"]),
        "tnx": float(row["TNX"]),
        "usdjpy": float(row["USDJPY"]),

        "tnx_change": float(row["TNX_change"]),
        "usdjpy_change": float(row["USDJPY_change"]),
    }


def evaluate_next_day(
    today,
    tomorrow,
    recommendation
):
    """
    今日のおすすめが翌日のQQQの値動きに対して
    良かったかどうかを判定する。
    """

    change = (
        (tomorrow["QQQ"] - today["QQQ"])
        / today["QQQ"]
        * 100
    )

    # 現時点では簡易評価
    #
    # 上昇 → 通常の強気系がおおむね有利
    # 下落 → 逆チャレンジ・ゴールド等が有利
    #
    # 後でrecommend_courses()に合わせて
    # 正式な判定ロジックに変更する。

    if recommendation in [
        "テクノロジー",
        "テクノロジーチャレンジ",
        "チャレンジ",
        "スタンダード",
    ]:

        result = "Win" if change > 0 else "Lose"

    elif recommendation in [
        "逆チャレンジ",
        "ゴールド",
        "アメリカ長期国債チャレンジ",
    ]:

        result = "Win" if change < 0 else "Lose"

    else:

        result = "Pending"

    return change, result


def run_backtest(period="5y"):

    print("=" * 50)
    print("📊 PayPay AI バックテスト")
    print("=" * 50)

    df = load_market_history(period)

    df = prepare_indicators(df)

    results = []

    # MA75などが計算できるまで待つ
    df = df.dropna()

    print(
        f"🔎 検証対象日数: {len(df)}"
    )

    for i in range(len(df) - 1):

        today = df.iloc[i]
        tomorrow = df.iloc[i + 1]

        try:

            market_data = make_market_data(
                today
            )

            market_score, reasons = score_market(
                market_data
            )

            ranking = recommend_courses(
                market_data,
                market_score
            )

            recommendation = ranking[0][0]

            next_change, result = evaluate_next_day(
                today,
                tomorrow,
                recommendation
            )

            results.append({
                "date": str(df.index[i].date()),

                # 市場スコア
                "score": market_score,

                # 当日の市場データ
                "qqq_change": round(
                    (df["QQQ"].iloc[i] / df["QQQ"].iloc[i - 1] - 1) * 100,
                    4
                ),

                "spy_change": round(
                    (df["SPY"].iloc[i] / df["SPY"].iloc[i - 1] - 1) * 100,
                    4
                ),

                "vix": round(
                    float(df["VIX"].iloc[i]),
                    4
                ),

                "gold_change": round(
                    (df["GLD"].iloc[i] / df["GLD"].iloc[i - 1] - 1) * 100,
                    4
                ),

                "tnx_change": round(
                    (df["TNX"].iloc[i] / df["TNX"].iloc[i - 1] - 1) * 100,
                    4
                ),

                "usdjpy_change": round(
                    (df["USDJPY"].iloc[i] / df["USDJPY"].iloc[i - 1] - 1) * 100,
                    4
                ),

                # おすすめ
                "recommend": recommendation,

                # 翌日のQQQ
                "next_day_qqq": round(
                    next_change,
                    2
                ),

                # 勝敗
                "result": result
            })

        except Exception as e:

            print(
                f"⚠️ {df.index[i].date()} "
                f"スキップ: {e}"
            )

    result_df = pd.DataFrame(results)

    if result_df.empty:
        print("❌ バックテスト結果がありません")
        return

    # 勝敗集計
    wins = (
        result_df["result"] == "Win"
    ).sum()

    losses = (
        result_df["result"] == "Lose"
    ).sum()

    total = wins + losses

    if total > 0:
        win_rate = (
            wins / total * 100
        )
    else:
        win_rate = 0

    print()
    print("=" * 50)
    print("📊 バックテスト結果")
    print("=" * 50)

    print(
        f"検証回数 : {len(result_df)}"
    )

    print(
        f"勝ち     : {wins}"
    )

    print(
        f"負け     : {losses}"
    )

    print(
        f"勝率     : {win_rate:.1f}%"
    )

    print()
    print("📌 最後の10件")
    print()

    print(
        result_df.tail(10).to_string(
            index=False
        )
    )

    # 保存
    output = "data/backtest.csv"

    result_df.to_csv(
        output,
        index=False,
        encoding="utf-8"
    )

    print()
    print(
        f"💾 保存しました: {output}"
    )
    
    analyze_indicators(results)

    return result_df

def analyze_backtest():

    path = Path("data/backtest.csv")

    if not path.exists():
        print("❌ data/backtest.csv がありません")
        return

    df = pd.read_csv(path)

    if df.empty:
        print("❌ バックテストデータが空です")
        return

    df["score"] = pd.to_numeric(
        df["score"],
        errors="coerce"
    )

    df["next_day_qqq"] = pd.to_numeric(
        df["next_day_qqq"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "score",
            "next_day_qqq"
        ]
    )

    print()
    print("=" * 50)
    print("📊 PayPay AI バックテスト詳細分析")
    print("=" * 50)

    # ========================================
    # スコア帯別分析
    # ========================================

    print()
    print("📈 スコア帯別成績")
    print("-" * 50)

    score_ranges = [
        ("80〜100", 80, 100),
        ("60〜79", 60, 79),
        ("40〜59", 40, 59),
        ("20〜39", 20, 39),
        ("0〜19", 0, 19),
    ]

    for name, low, high in score_ranges:

        subset = df[
            (df["score"] >= low)
            & (df["score"] <= high)
        ]

        if len(subset) == 0:
            continue

        wins = (
            subset["next_day_qqq"] > 0
        ).sum()

        total = len(subset)

        win_rate = (
            wins / total * 100
        )

        avg_return = (
            subset["next_day_qqq"].mean()
        )

        print(
            f"{name:8} "
            f"{total:4}回 "
            f"勝率 {win_rate:5.1f}% "
            f"平均QQQ {avg_return:+.2f}%"
        )

    # ========================================
    # コース別分析
    # ========================================

    print()
    print("🏆 コース別成績")
    print("-" * 50)

    courses = sorted(
        df["recommend"]
        .dropna()
        .unique()
    )

    for course in courses:

        subset = df[
            df["recommend"] == course
        ]

        total = len(subset)

        if total == 0:
            continue

        wins = (
            subset["next_day_qqq"] > 0
        ).sum()

        win_rate = (
            wins / total * 100
        )

        avg_return = (
            subset["next_day_qqq"].mean()
        )

        print(
            f"{course:20} "
            f"{total:4}回 "
            f"勝率 {win_rate:5.1f}% "
            f"平均 {avg_return:+.2f}%"
        )

    # ========================================
    # 高スコア限定
    # ========================================

    print()
    print("🔥 高スコア限定")
    print("-" * 50)

    for threshold in [60, 70, 80]:

        subset = df[
            df["score"] >= threshold
        ]

        if len(subset) == 0:
            continue

        wins = (
            subset["next_day_qqq"] > 0
        ).sum()

        total = len(subset)

        win_rate = (
            wins / total * 100
        )

        avg_return = (
            subset["next_day_qqq"].mean()
        )

        print(
            f"スコア >= {threshold}: "
            f"{total}回 "
            f"勝率 {win_rate:.1f}% "
            f"平均QQQ {avg_return:+.2f}%"
        )

    # ========================================
    # 年別分析
    # ========================================

    print()
    print("📅 年別成績")
    print("-" * 50)

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df["year"] = df["date"].dt.year

    for year, subset in df.groupby("year"):

        total = len(subset)

        wins = (
            subset["next_day_qqq"] > 0
        ).sum()

        win_rate = (
            wins / total * 100
        )

        avg_return = (
            subset["next_day_qqq"].mean()
        )

        print(
            f"{year}: "
            f"{total:4}回 "
            f"勝率 {win_rate:5.1f}% "
            f"平均QQQ {avg_return:+.2f}%"
        )

    # ========================================
    # スコアと翌日QQQの相関
    # ========================================

    correlation = df[
        [
            "score",
            "next_day_qqq"
        ]
    ].corr().iloc[0, 1]

    print()
    print("🔬 スコアと翌日QQQの相関")
    print("-" * 50)

    print(
        f"相関係数: {correlation:.3f}"
    )

    # ========================================
    # CSV保存
    # ========================================

    output = Path(
        "data/backtest_analysis.csv"
    )

    rows = []

    for name, low, high in score_ranges:

        subset = df[
            (df["score"] >= low)
            & (df["score"] <= high)
        ]

        if len(subset) == 0:
            continue

        wins = (
            subset["next_day_qqq"] > 0
        ).sum()

        total = len(subset)

        rows.append({
            "type": "score_range",
            "name": name,
            "count": total,
            "win_rate": round(
                wins / total * 100,
                2
            ),
            "avg_next_day_qqq": round(
                subset[
                    "next_day_qqq"
                ].mean(),
                4
            )
        })

    pd.DataFrame(
        rows
    ).to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"💾 分析結果保存: {output}"
    )
    
# ============================================================
# 指標別有効性分析
# ============================================================

def analyze_indicators(results):

    df = pd.DataFrame(results)

    print()
    print("=== analyze_indicators received columns ===")
    print(df.columns.tolist())

    print()
    print("=" * 50)
    print("📊 指標別の有効性分析")
    print("=" * 50)

    df = pd.DataFrame(results)

    indicators = [
        "qqq_change",
        "spy_change",
        "vix",
        "gold_change",
        "tnx_change",
        "usdjpy_change",
    ]

    names = {
        "qqq_change": "QQQ",
        "spy_change": "S&P500",
        "vix": "VIX",
        "gold_change": "Gold",
        "tnx_change": "10年金利",
        "usdjpy_change": "ドル円",
    }

    analysis = []

    for indicator in indicators:

        if indicator not in df.columns:
            print(
                f"⚠️ {names[indicator]}: "
                f"列なし"
            )
            continue

        temp = df[
            [indicator, "next_day_qqq"]
        ].dropna()

        if len(temp) < 20:
            print(
                f"⚠️ {names[indicator]}: "
                f"データ不足 ({len(temp)}件)"
            )
            continue

        # 相関
        correlation = temp[indicator].corr(
            temp["next_day_qqq"]
        )

        # 中央値
        median = temp[indicator].median()

        high = temp[
            temp[indicator] >= median
        ]["next_day_qqq"]

        low = temp[
            temp[indicator] < median
        ]["next_day_qqq"]

        high_avg = high.mean()
        low_avg = low.mean()

        difference = high_avg - low_avg

        # 上昇した日の翌日勝率
        positive = temp[
            temp[indicator] > 0
        ]["next_day_qqq"]

        # 下落した日の翌日勝率
        negative = temp[
            temp[indicator] < 0
        ]["next_day_qqq"]

        positive_win_rate = (
            (positive > 0).mean() * 100
            if len(positive) > 0
            else None
        )

        negative_win_rate = (
            (negative > 0).mean() * 100
            if len(negative) > 0
            else None
        )

        analysis.append({

            "indicator":
                names[indicator],

            "samples":
                len(temp),

            "correlation":
                round(
                    correlation,
                    4
                ),

            "high_avg_qqq":
                round(
                    high_avg,
                    4
                ),

            "low_avg_qqq":
                round(
                    low_avg,
                    4
                ),

            "difference":
                round(
                    difference,
                    4
                ),

            "positive_samples":
                len(positive),

            "positive_win_rate":
                round(
                    positive_win_rate,
                    2
                )
                if positive_win_rate is not None
                else None,

            "negative_samples":
                len(negative),

            "negative_win_rate":
                round(
                    negative_win_rate,
                    2
                )
                if negative_win_rate is not None
                else None,
        })

        print(
            f"{names[indicator]:<12}"
            f"相関 {correlation:+.4f}  "
            f"高値側 {high_avg:+.2f}%  "
            f"低値側 {low_avg:+.2f}%  "
            f"差 {difference:+.2f}%"
        )

        if positive_win_rate is not None:
            print(
                f"             "
                f"上昇後勝率 "
                f"{positive_win_rate:.1f}%"
            )

        if negative_win_rate is not None:
            print(
                f"             "
                f"下落後勝率 "
                f"{negative_win_rate:.1f}%"
            )

    result_df = pd.DataFrame(
        analysis
    )

    result_df.to_csv(
        "data/indicator_analysis.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        "💾 保存しました: "
        "data/indicator_analysis.csv"
    )

    return result_df

def train_test_split(df, train_ratio=0.8):

    split_index = int(
        len(df) * train_ratio
    )

    train = df.iloc[:split_index].copy()

    test = df.iloc[split_index:].copy()

    print()
    print("=" * 50)
    print("📊 Train / Test 分離")
    print("=" * 50)

    print(
        f"TRAIN : "
        f"{train.index[0].date()} "
        f"～ "
        f"{train.index[-1].date()}"
    )

    print(
        f"TEST  : "
        f"{test.index[0].date()} "
        f"～ "
        f"{test.index[-1].date()}"
    )

    print(
        f"TRAIN件数 : {len(train)}"
    )

    print(
        f"TEST件数  : {len(test)}"
    )

    return train, test

if __name__ == "__main__":
    run_backtest("5y")
    analyze_backtest()