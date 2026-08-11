from pathlib import Path

import pandas as pd
import numpy as np


BACKTEST_FILE = Path("data/backtest.csv")


def load_backtest():

    if not BACKTEST_FILE.exists():

        raise FileNotFoundError(
            f"{BACKTEST_FILE} がありません"
        )

    df = pd.read_csv(BACKTEST_FILE)

    df["date"] = pd.to_datetime(df["date"])

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
            "date",
            "score",
            "next_day_qqq"
        ]
    )

    return df.sort_values("date").reset_index(drop=True)


# ========================================
# 基本成績
# ========================================

def evaluate(df, name):

    if len(df) == 0:
        return

    wins = (df["next_day_qqq"] > 0).sum()

    total = len(df)

    win_rate = wins / total * 100

    avg = df["next_day_qqq"].mean()

    print()
    print("=" * 50)
    print(name)
    print("=" * 50)

    print(f"検証回数 : {total}")
    print(f"勝ち     : {wins}")
    print(f"負け     : {total - wins}")
    print(f"勝率     : {win_rate:.1f}%")
    print(f"平均QQQ  : {avg:+.3f}%")


# ========================================
# Train / Test
# ========================================

def train_test_split(df):

    split_index = int(len(df) * 0.8)

    train = df.iloc[:split_index].copy()

    test = df.iloc[split_index:].copy()

    return train, test


# ========================================
# スコア帯分析
# ========================================

def score_analysis(df):

    print()
    print("=" * 50)
    print("📊 スコア帯分析")
    print("=" * 50)

    bins = [
        0,
        20,
        40,
        60,
        80,
        101
    ]

    labels = [
        "0〜19",
        "20〜39",
        "40〜59",
        "60〜79",
        "80〜100"
    ]

    temp = df.copy()

    temp["score_band"] = pd.cut(
        temp["score"],
        bins=bins,
        labels=labels,
        right=False
    )

    result = (
        temp
        .groupby("score_band", observed=False)
        .agg(
            count=("next_day_qqq", "size"),
            win_rate=(
                "next_day_qqq",
                lambda x: (x > 0).mean() * 100
            ),
            average_qqq=(
                "next_day_qqq",
                "mean"
            )
        )
    )

    print(result.round(3))

    return result


# ========================================
# 高スコア検証
# ========================================

def threshold_analysis(df):

    print()
    print("=" * 50)
    print("🔥 スコア閾値分析")
    print("=" * 50)

    rows = []

    for threshold in [
        50,
        55,
        60,
        65,
        70,
        75,
        80
    ]:

        subset = df[
            df["score"] >= threshold
        ]

        if len(subset) == 0:
            continue

        win_rate = (
            subset["next_day_qqq"] > 0
        ).mean() * 100

        avg = subset["next_day_qqq"].mean()

        rows.append({
            "threshold": threshold,
            "count": len(subset),
            "win_rate": win_rate,
            "average_qqq": avg
        })

    result = pd.DataFrame(rows)

    print(result.round(3))

    return result


# ========================================
# スコアと翌日QQQ
# ========================================

def correlation_analysis(df):

    print()
    print("=" * 50)
    print("🔬 スコア相関分析")
    print("=" * 50)

    corr = df[
        ["score", "next_day_qqq"]
    ].corr()

    print(corr.round(4))

    return corr


# ========================================
# Train / Test
# ========================================

def run():

    print("=" * 50)
    print("📊 PayPay AI Backtest v2")
    print("=" * 50)

    df = load_backtest()

    print(
        f"データ期間: "
        f"{df['date'].min().date()} ～ "
        f"{df['date'].max().date()}"
    )

    print(
        f"総件数: {len(df)}"
    )

    # ====================================
    # Train / Test
    # ====================================

    train, test = train_test_split(df)

    print()
    print("=" * 50)
    print("🧪 Train / Test 分離")
    print("=" * 50)

    print(
        f"Train: "
        f"{train['date'].min().date()} ～ "
        f"{train['date'].max().date()}"
    )

    print(
        f"Test : "
        f"{test['date'].min().date()} ～ "
        f"{test['date'].max().date()}"
    )

    print(
        f"Train件数: {len(train)}"
    )

    print(
        f"Test件数 : {len(test)}"
    )

    # ====================================
    # Train
    # ====================================

    evaluate(
        train,
        "🧠 TRAIN 成績"
    )

    score_analysis(train)

    threshold_analysis(train)

    correlation_analysis(train)

    # ====================================
    # Test
    # ====================================

    evaluate(
        test,
        "🚀 TEST 成績"
    )

    score_analysis(test)

    threshold_analysis(test)

    correlation_analysis(test)

    # ====================================
    # 保存
    # ====================================

    output = Path(
        "data/backtest_v2_summary.csv"
    )

    summary = pd.DataFrame({

        "dataset": [
            "train",
            "test"
        ],

        "count": [
            len(train),
            len(test)
        ],

        "win_rate": [
            (train["next_day_qqq"] > 0).mean() * 100,
            (test["next_day_qqq"] > 0).mean() * 100
        ],

        "average_qqq": [
            train["next_day_qqq"].mean(),
            test["next_day_qqq"].mean()
        ]
    })

    summary.to_csv(
        output,
        index=False
    )

    print()
    print(
        f"💾 保存しました: {output}"
    )


if __name__ == "__main__":
    run()