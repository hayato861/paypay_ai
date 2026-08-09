import pandas as pd
import numpy as np
from pathlib import Path

INPUT_FILE = Path("data/backtest.csv")
OUTPUT_FILE = Path("data/backtest_analysis.csv")
STRATEGY_FILE = Path("data/backtest_strategy.csv")

# ============================================================
# データ読み込み
# ============================================================

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} が見つかりません"
        )

    df = pd.read_csv(INPUT_FILE)

    required = [
        "date",
        "score",
        "recommend",
        "next_day_qqq",
        "result"
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"必要な列がありません: {missing}"
        )

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
    ).copy()

    df = df.sort_values("date").reset_index(drop=True)

    return df

# ============================================================
# 基本統計
# ============================================================

def performance_stats(returns):
    
    returns = pd.Series(returns).dropna()
    if len(returns) == 0:
        return {
            "count": 0,
            "win_rate": np.nan,
            "mean": np.nan,
            "median": np.nan,
            "cumulative": np.nan,
            "max_drawdown": np.nan,
        }

    win_rate = (
        (returns > 0).mean()
        * 100
    )

    mean_return = returns.mean()
    median_return = returns.median()
    cumulative = (
        (1 + returns / 100)
        .prod()
        - 1
    ) * 100

    equity = (
        1 + returns / 100
    ).cumprod()

    peak = equity.cummax()

    drawdown = (
        equity / peak - 1
    ) * 100

    max_drawdown = drawdown.min()

    return {
        "count": len(returns),
        "win_rate": win_rate,
        "mean": mean_return,
        "median": median_return,
        "cumulative": cumulative,
        "max_drawdown": max_drawdown,
    }

# ============================================================
# 表示
# ============================================================

def print_stats(title, stats):

    print()
    print(title)
    print("-" * 50)
    print(
        f"回数       : {stats['count']}"
    )

    print(
        f"勝率       : {stats['win_rate']:.1f}%"
    )

    print(
        f"平均QQQ    : {stats['mean']:+.3f}%"
    )

    print(
        f"中央値     : {stats['median']:+.3f}%"
    )

    print(
        f"累積リターン: {stats['cumulative']:+.2f}%"
    )

    print(
        f"最大DD     : {stats['max_drawdown']:.2f}%"
    )


# ============================================================
# スコア帯分析
# ============================================================

def score_band_analysis(df):

    bins = [
        -1,
        19,
        39,
        59,
        69,
        79,
        100
    ]

    labels = [
        "0〜19",
        "20〜39",
        "40〜59",
        "60〜69",
        "70〜79",
        "80〜100"
    ]

    df["score_band"] = pd.cut(
        df["score"],
        bins=bins,
        labels=labels
    )

    print()
    print("📊 スコア帯別分析")
    print("=" * 60)

    rows = []

    for band in labels:

        subset = df[
            df["score_band"] == band
        ]

        if len(subset) == 0:
            continue

        stats = performance_stats(
            subset["next_day_qqq"]
        )

        print()
        print(
            f"{band:8s}"
            f" {stats['count']:4d}回"
            f" 勝率 {stats['win_rate']:5.1f}%"
            f" 平均 {stats['mean']:+.3f}%"
            f" 中央値 {stats['median']:+.3f}%"
            f" 累積 {stats['cumulative']:+.2f}%"
        )

        rows.append({
            "type": "score_band",
            "group": band,
            **stats
        })

    return rows


# ============================================================
# スコア閾値戦略
#
# 例:
# score >= 70 の日だけQQQを保有
# それ以外は現金
# ============================================================

def threshold_analysis(df):

    print()
    print("🔥 スコア閾値戦略")
    print("=" * 60)

    rows = []

    # 全期間BUY & HOLD
    buy_hold = performance_stats(
        df["next_day_qqq"]
    )

    print_stats(
        "📌 BUY & HOLD（毎日QQQ）",
        buy_hold
    )

    rows.append({
        "type": "buy_hold",
        "threshold": None,
        **buy_hold
    })

    for threshold in [
        40,
        50,
        60,
        65,
        70,
        75,
        80
    ]:

        selected = df[
            df["score"] >= threshold
        ]

        if len(selected) == 0:
            continue

        stats = performance_stats(
            selected["next_day_qqq"]
        )

        print()
        print(
            f"スコア >= {threshold}"
        )

        print(
            f"  回数       : {stats['count']}"
        )

        print(
            f"  勝率       : {stats['win_rate']:.1f}%"
        )

        print(
            f"  平均QQQ    : {stats['mean']:+.3f}%"
        )

        print(
            f"  累積リターン: {stats['cumulative']:+.2f}%"
        )

        print(
            f"  最大DD     : {stats['max_drawdown']:.2f}%"
        )

        rows.append({
            "type": "threshold",
            "threshold": threshold,
            **stats
        })

    return rows


# ============================================================
# コース別分析
# ============================================================

def course_analysis(df):

    print()
    print("🏆 コース別分析")
    print("=" * 60)

    rows = []

    for course, subset in df.groupby(
        "recommend"
    ):

        stats = performance_stats(
            subset["next_day_qqq"]
        )

        print()
        print(course)

        print(
            f"  回数       : {stats['count']}"
        )

        print(
            f"  勝率       : {stats['win_rate']:.1f}%"
        )

        print(
            f"  平均QQQ    : {stats['mean']:+.3f}%"
        )

        print(
            f"  中央値     : {stats['median']:+.3f}%"
        )

        print(
            f"  累積       : {stats['cumulative']:+.2f}%"
        )

        print(
            f"  最大DD     : {stats['max_drawdown']:.2f}%"
        )

        rows.append({
            "type": "course",
            "group": course,
            **stats
        })

    return rows


# ============================================================
# 年別分析
# ============================================================

def yearly_analysis(df):

    print()
    print("📅 年別分析")
    print("=" * 60)

    rows = []

    df["year"] = df["date"].dt.year

    for year, subset in df.groupby(
        "year"
    ):

        stats = performance_stats(
            subset["next_day_qqq"]
        )

        print(
            f"{year}: "
            f"{stats['count']:4d}回 "
            f"勝率 {stats['win_rate']:5.1f}% "
            f"平均 {stats['mean']:+.3f}% "
            f"累積 {stats['cumulative']:+.2f}%"
        )

        rows.append({
            "type": "year",
            "group": year,
            **stats
        })

    return rows


# ============================================================
# スコアと翌日QQQの関係
# ============================================================

def correlation_analysis(df):

    correlation = df[
        ["score", "next_day_qqq"]
    ].corr().iloc[0, 1]

    print()
    print("🔬 スコアと翌日QQQ")
    print("=" * 60)

    print(
        f"相関係数 : {correlation:+.4f}"
    )

    return correlation


# ============================================================
# 前半・後半比較
# ============================================================

def period_analysis(df):

    print()
    print("🧪 前半・後半比較")
    print("=" * 60)

    midpoint = len(df) // 2

    first = df.iloc[:midpoint]

    second = df.iloc[midpoint:]

    first_stats = performance_stats(
        first["next_day_qqq"]
    )

    second_stats = performance_stats(
        second["next_day_qqq"]
    )

    print()
    print("前半")

    print(
        f"期間       : "
        f"{first['date'].min().date()} ～ "
        f"{first['date'].max().date()}"
    )

    print(
        f"勝率       : "
        f"{first_stats['win_rate']:.1f}%"
    )

    print(
        f"平均QQQ    : "
        f"{first_stats['mean']:+.3f}%"
    )

    print()
    print("後半")

    print(
        f"期間       : "
        f"{second['date'].min().date()} ～ "
        f"{second['date'].max().date()}"
    )

    print(
        f"勝率       : "
        f"{second_stats['win_rate']:.1f}%"
    )

    print(
        f"平均QQQ    : "
        f"{second_stats['mean']:+.3f}%"
    )


# ============================================================
# まとめ
# ============================================================

def final_judgement(df):

    correlation = df[
        ["score", "next_day_qqq"]
    ].corr().iloc[0, 1]

    high = df[
        df["score"] >= 70
    ]

    all_stats = performance_stats(
        df["next_day_qqq"]
    )

    high_stats = performance_stats(
        high["next_day_qqq"]
    )

    print()
    print("🤖 AI評価")
    print("=" * 60)

    print(
        f"全体平均QQQ : "
        f"{all_stats['mean']:+.3f}%"
    )

    print(
        f"70点以上平均: "
        f"{high_stats['mean']:+.3f}%"
    )

    print(
        f"70点以上勝率: "
        f"{high_stats['win_rate']:.1f}%"
    )

    print(
        f"スコア相関   : "
        f"{correlation:+.4f}"
    )

    print()

    if (
        high_stats["win_rate"]
        > all_stats["win_rate"] + 5
        and high_stats["mean"]
        > all_stats["mean"]
    ):

        print(
            "✅ 70点以上に一定の有効性が見られます"
        )

    elif high_stats["mean"] > all_stats["mean"]:

        print(
            "🟡 70点以上の平均リターンは改善しています"
        )

    else:

        print(
            "⚠️ 現在のスコアには明確な予測力が確認できません"
        )

# ============================================================
# メイン
# ============================================================

def run_analysis():
    print("=" * 60)
    print("📊 PayPay AI バックテスト分析 v2")
    print("=" * 60)

    df = load_data()

    print()
    print(
        f"📥 データ読み込み: {len(df)}件"
    )
    print(
        f"期間: "
        f"{df['date'].min().date()} ～ "
        f"{df['date'].max().date()}"
    )

    all_rows = []

    all_rows.extend(
        score_band_analysis(df)
    )
    all_rows.extend(
        threshold_analysis(df)
    )
    all_rows.extend(
        course_analysis(df)
    )
    all_rows.extend(
        yearly_analysis(df)
    )

    correlation = correlation_analysis(df)

    period_analysis(df)
    final_judgement(df)

    # 分析結果保存
    result_df = pd.DataFrame(
        all_rows
    )

    result_df["correlation"] = correlation

    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )
    print()
    print(
        f"💾 分析結果保存: {OUTPUT_FILE}"
    )

if __name__ == "__main__":
    run_analysis()