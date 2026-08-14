import os
import numpy as np
import pandas as pd


# ============================================================
# PayPay AI Signal Analysis v2.17
# ============================================================
#
# Purpose:
#   v2.16で発見された DOWN_BOTH 構造の頑健性を検証する。
#
# Main checks:
#   1. Fixed DOWN_BOTH strategy
#   2. Threshold sensitivity
#   3. Walk-forward stability
#   4. Bootstrap robustness
#   5. Permutation test
#
# IMPORTANT:
#   このバージョンでは全期間を使って最適な閾値を選ばない。
#   閾値はあくまで感度分析として固定評価する。
#
# ============================================================


VERSION = "v2.17"

INPUT_FILE = "data/ai_ml_comparison_v1_9.csv"

OUTPUT_DIR = "data"

INITIAL_CAPITAL = 100_000

# Transaction cost per trade (%)
TRANSACTION_COST_PCT = 0.05

# Walk-forward
INITIAL_TRAIN = 100
VALIDATION_SIZE = 40
STEP = 40

# Bootstrap
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 42

# Permutation
PERMUTATION_ITERATIONS = 5_000
PERMUTATION_SEED = 123

# DOWN threshold sensitivity
DOWN_THRESHOLDS = [0.45, 0.475, 0.50, 0.525, 0.55]


# ============================================================
# Utility
# ============================================================

def print_header(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def safe_float(value):
    try:
        value = float(value)

        if not np.isfinite(value):
            return np.nan

        return value

    except Exception:
        return np.nan


# ============================================================
# Load
# ============================================================

def load_data():

    print_header("📥 SIGNAL DATA")

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"ファイル : {INPUT_FILE}")
    print(f"件数     : {len(df)}")

    print()
    print("📋 CSV COLUMNS")
    print(list(df.columns))

    required_columns = [
        "date",
        "ai_probability",
        "ml_probability",
        "next_day_qqq",
        "actual",
        "ai_direction",
        "ml_direction",
    ]

    missing = [
        c for c in required_columns
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}"
        )

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    for col in [
        "ai_probability",
        "ml_probability",
        "next_day_qqq",
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna(
        subset=[
            "date",
            "ai_probability",
            "ml_probability",
            "next_day_qqq",
        ]
    ).reset_index(drop=True)

    print()
    print(
        f"期間 : "
        f"{df['date'].min().date()} ～ "
        f"{df['date'].max().date()}"
    )

    print(f"最終件数 : {len(df)}")

    return df


# ============================================================
# Signal calculation
# ============================================================

def calculate_signals(df):

    df = df.copy()

    # Probability difference from neutral 50%
    df["ai_probability_pct"] = (
        df["ai_probability"] * 100
    )

    df["ml_probability_pct"] = (
        df["ml_probability"] * 100
    )

    # Recalculate directions from probability.
    #
    # This avoids depending on an old direction definition
    # contained in the source CSV.
    #
    df["ai_direction_calc"] = np.where(
        df["ai_probability"] >= 0.50,
        "UP",
        "DOWN"
    )

    df["ml_direction_calc"] = np.where(
        df["ml_probability"] >= 0.50,
        "UP",
        "DOWN"
    )

    df["direction"] = np.select(
        [
            (
                (df["ai_direction_calc"] == "UP")
                &
                (df["ml_direction_calc"] == "UP")
            ),
            (
                (df["ai_direction_calc"] == "DOWN")
                &
                (df["ml_direction_calc"] == "DOWN")
            ),
        ],
        [
            "UP",
            "DOWN",
        ],
        default="CONFLICT"
    )

    df["agreement"] = (
        df["direction"] != "CONFLICT"
    )

    # Probability gap
    df["probability_gap"] = (
        df["ai_probability"]
        -
        df["ml_probability"]
    ).abs()

    # Joint distance from neutral
    df["ai_distance"] = (
        df["ai_probability"] - 0.50
    ).abs()

    df["ml_distance"] = (
        df["ml_probability"] - 0.50
    ).abs()

    df["strength"] = (
        (
            df["ai_distance"]
            +
            df["ml_distance"]
        )
        * 100
    )

    # Fixed v2.16 strategy:
    #
    # AI DOWN + ML DOWN
    #
    df["down_both"] = (
        (df["ai_probability"] < 0.50)
        &
        (df["ml_probability"] < 0.50)
    )

    # Contrarian interpretation:
    #
    # Both models say DOWN
    # -> strategy goes LONG / UP
    #
    df["signal"] = np.where(
        df["down_both"],
        "CONTRARIAN_UP",
        "HOLD"
    )

    return df


# ============================================================
# Signal integrity
# ============================================================

def signal_integrity(df):

    print_header("🔎 SIGNAL INTEGRITY")

    print()
    print("AI probability")

    print(
        df["ai_probability"].describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
            ]
        ).round(4)
    )

    print()
    print("ML probability")

    print(
        df["ml_probability"].describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
            ]
        ).round(4)
    )

    print()
    print("Direction")

    print(
        df["direction"].value_counts()
    )

    print()
    print("Strength")

    print(
        df["strength"].describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
            ]
        ).round(4)
    )

    print()
    print("Return")

    print(
        df["next_day_qqq"].describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
            ]
        ).round(4)
    )

    invalid = {}

    for col in [
        "ai_probability",
        "ml_probability",
        "strength",
        "next_day_qqq",
    ]:
        invalid[col] = int(
            (
                ~np.isfinite(
                    df[col].astype(float)
                )
            ).sum()
        )

    print()
    print("Invalid / inf / nan")

    for key, value in invalid.items():
        print(f"{key:20s} {value}")

    if any(v > 0 for v in invalid.values()):
        raise ValueError(
            "Signal integrity check failed."
        )

    print()
    print("✅ Signal integrity check passed")


# ============================================================
# Strategy performance
# ============================================================

def calculate_performance(
    returns,
    transaction_cost_pct=TRANSACTION_COST_PCT
):

    returns = pd.Series(
        returns,
        dtype=float
    )

    returns = returns.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if len(returns) == 0:
        return {
            "return": np.nan,
            "max_dd": np.nan,
            "win_rate": np.nan,
            "trades": 0,
            "mean_trade": np.nan,
            "profit_factor": np.nan,
            "sharpe": np.nan,
            "sortino": np.nan,
            "final_capital": np.nan,
        }

    net_returns = (
        returns
        -
        transaction_cost_pct
    )

    equity = (
        1
        +
        net_returns / 100
    ).cumprod()

    initial = 1.0

    final_value = equity.iloc[-1]

    total_return = (
        final_value / initial - 1
    ) * 100

    running_max = equity.cummax()

    drawdown = (
        equity / running_max - 1
    ) * 100

    max_dd = drawdown.min()

    win_rate = (
        (net_returns > 0).mean()
        * 100
    )

    gain = (
        net_returns[
            net_returns > 0
        ].sum()
    )

    loss = abs(
        net_returns[
            net_returns < 0
        ].sum()
    )

    if loss == 0:
        if gain > 0:
            profit_factor = np.inf
        else:
            profit_factor = np.nan
    else:
        profit_factor = gain / loss

    mean_return = net_returns.mean()

    std_return = net_returns.std(
        ddof=1
    )

    if (
        std_return > 0
        and np.isfinite(std_return)
    ):
        sharpe = (
            mean_return
            /
            std_return
        ) * np.sqrt(252)

    else:
        sharpe = np.nan

    downside = net_returns[
        net_returns < 0
    ]

    downside_std = downside.std(
        ddof=1
    )

    if (
        downside_std > 0
        and np.isfinite(downside_std)
    ):
        sortino = (
            mean_return
            /
            downside_std
        ) * np.sqrt(252)

    elif mean_return > 0:
        sortino = np.inf

    else:
        sortino = np.nan

    final_capital = (
        INITIAL_CAPITAL
        * final_value
    )

    return {
        "return": total_return,
        "max_dd": max_dd,
        "win_rate": win_rate,
        "trades": len(net_returns),
        "mean_trade": mean_return,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "sortino": sortino,
        "final_capital": final_capital,
    }


# ============================================================
# Fixed DOWN_BOTH
# ============================================================

def evaluate_fixed_strategy(df):

    print_header("🎯 FIXED DOWN_BOTH STRATEGY")

    trades = df.loc[
        df["down_both"]
    ].copy()

    print(
        f"DOWN_BOTH trades : {len(trades)}"
    )

    if len(trades) == 0:
        print("No trades.")
        return None

    perf = calculate_performance(
        trades["next_day_qqq"]
    )

    print()
    print(
        f"Return       : {perf['return']:+.2f}%"
    )

    print(
        f"MaxDD        : {perf['max_dd']:+.2f}%"
    )

    print(
        f"WinRate      : {perf['win_rate']:.1f}%"
    )

    print(
        f"Trades       : {perf['trades']}"
    )

    print(
        f"Mean trade   : {perf['mean_trade']:+.3f}%"
    )

    print(
        f"PF           : {perf['profit_factor']:.2f}"
        if np.isfinite(perf["profit_factor"])
        else
        f"PF           : {perf['profit_factor']}"
    )

    print(
        f"Sharpe       : {perf['sharpe']:.2f}"
        if np.isfinite(perf["sharpe"])
        else
        f"Sharpe       : {perf['sharpe']}"
    )

    print(
        f"Sortino      : {perf['sortino']:.2f}"
        if np.isfinite(perf["sortino"])
        else
        f"Sortino      : {perf['sortino']}"
    )

    return trades, perf


# ============================================================
# Threshold sensitivity
# ============================================================

def threshold_sensitivity(df):

    print_header("🔬 THRESHOLD SENSITIVITY")

    rows = []

    for threshold in DOWN_THRESHOLDS:

        signal = (
            (df["ai_probability"] < threshold)
            &
            (df["ml_probability"] < threshold)
        )

        selected = df.loc[
            signal
        ]

        perf = calculate_performance(
            selected["next_day_qqq"]
        )

        rows.append({
            "threshold": threshold,
            "threshold_pct": threshold * 100,
            "count": len(selected),
            "mean_return": (
                selected["next_day_qqq"].mean()
                if len(selected) > 0
                else np.nan
            ),
            "win_rate": perf["win_rate"],
            "strategy_return": perf["return"],
            "max_dd": perf["max_dd"],
            "profit_factor": perf["profit_factor"],
            "sharpe": perf["sharpe"],
        })

    result = pd.DataFrame(rows)

    print(
        result.round(4).to_string(
            index=False
        )
    )

    return result


# ============================================================
# Candidate strategy definitions
# ============================================================

def create_strategy_signal(
    df,
    strategy_name,
    threshold=0.50
):

    ai_up = (
        df["ai_probability"] >= threshold
    )

    ml_up = (
        df["ml_probability"] >= threshold
    )

    ai_down = ~ai_up
    ml_down = ~ml_up

    if strategy_name == "DOWN_BOTH":

        return (
            ai_down
            &
            ml_down
        )

    if strategy_name == "AI_DOWN_ONLY":

        return ai_down

    if strategy_name == "ML_DOWN_ONLY":

        return ml_down

    if strategy_name == "AI_UP_ML_DOWN":

        return (
            ai_up
            &
            ml_down
        )

    if strategy_name == "AI_DOWN_ML_UP":

        return (
            ai_down
            &
            ml_up
        )

    if strategy_name == "ALL_DAYS":

        return pd.Series(
            True,
            index=df.index
        )

    raise ValueError(
        f"Unknown strategy: {strategy_name}"
    )


# ============================================================
# Walk-forward
# ============================================================

def walk_forward_strategy(
    df,
    strategy_name="DOWN_BOTH",
    threshold=0.50
):

    print_header(
        f"🚶 WALK-FORWARD : {strategy_name}"
    )

    results = []

    n = len(df)

    fold = 1

    train_end = INITIAL_TRAIN

    while (
        train_end + VALIDATION_SIZE
        <= n
    ):

        train = df.iloc[
            :train_end
        ].copy()

        validation = df.iloc[
            train_end:
            train_end + VALIDATION_SIZE
        ].copy()

        print()
        print("=" * 70)
        print(f"FOLD {fold}")
        print("=" * 70)

        print(
            f"Train : "
            f"{train['date'].min().date()} ～ "
            f"{train['date'].max().date()} "
            f"({len(train)})"
        )

        print(
            f"Validation : "
            f"{validation['date'].min().date()} ～ "
            f"{validation['date'].max().date()} "
            f"({len(validation)})"
        )

        # IMPORTANT:
        #
        # The strategy is fixed.
        #
        # We do NOT use validation data
        # to choose anything.
        #
        validation_signal = (
            create_strategy_signal(
                validation,
                strategy_name,
                threshold
            )
        )

        trades = validation.loc[
            validation_signal
        ].copy()

        perf = calculate_performance(
            trades["next_day_qqq"]
        )

        print()
        print(
            f"Strategy : {strategy_name}"
        )

        print(
            f"Threshold : {threshold:.3f}"
        )

        print()
        print(
            f"Return   : "
            f"{perf['return']:+.2f}%"
        )

        print(
            f"MaxDD    : "
            f"{perf['max_dd']:+.2f}%"
        )

        print(
            f"WinRate  : "
            f"{perf['win_rate']:.1f}%"
        )

        print(
            f"Trades   : "
            f"{perf['trades']}"
        )

        print(
            f"Sharpe   : "
            f"{perf['sharpe']:.2f}"
            if np.isfinite(perf["sharpe"])
            else
            f"Sharpe   : {perf['sharpe']}"
        )

        print(
            f"PF       : "
            f"{perf['profit_factor']:.2f}"
            if np.isfinite(perf["profit_factor"])
            else
            f"PF       : {perf['profit_factor']}"
        )

        results.append({
            "fold": fold,
            "validation_start": validation["date"].min(),
            "validation_end": validation["date"].max(),
            "strategy": strategy_name,
            "threshold": threshold,
            "return": perf["return"],
            "max_dd": perf["max_dd"],
            "win_rate": perf["win_rate"],
            "trades": perf["trades"],
            "sharpe": perf["sharpe"],
            "sortino": perf["sortino"],
            "profit_factor": perf["profit_factor"],
        })

        fold += 1

        train_end += STEP

    return pd.DataFrame(results)


# ============================================================
# Combined OOS
# ============================================================

def combined_oos(
    df,
    strategy_name,
    threshold
):

    print_header(
        f"🏁 OUT-OF-SAMPLE TOTAL : {strategy_name}"
    )

    n = len(df)

    train_end = INITIAL_TRAIN

    all_oos = []

    fold = 1

    while (
        train_end + VALIDATION_SIZE
        <= n
    ):

        validation = df.iloc[
            train_end:
            train_end + VALIDATION_SIZE
        ].copy()

        signal = create_strategy_signal(
            validation,
            strategy_name,
            threshold
        )

        validation["selected"] = signal

        validation["strategy_return"] = np.where(
            signal,
            validation["next_day_qqq"],
            0.0
        )

        validation["fold"] = fold

        all_oos.append(
            validation
        )

        fold += 1

        train_end += STEP

    if not all_oos:
        return None

    oos = pd.concat(
        all_oos,
        ignore_index=True
    )

    trades = oos.loc[
        oos["selected"]
    ].copy()

    perf = calculate_performance(
        trades["next_day_qqq"]
    )

    print(
        f"初期資金       : "
        f"{INITIAL_CAPITAL:,.0f}"
    )

    print(
        f"最終資金       : "
        f"{perf['final_capital']:,.0f}"
    )

    print(
        f"累積リターン   : "
        f"{perf['return']:+.2f}%"
    )

    print(
        f"取引回数       : "
        f"{perf['trades']}"
    )

    print(
        f"勝率           : "
        f"{perf['win_rate']:.1f}%"
    )

    print(
        f"平均取引       : "
        f"{perf['mean_trade']:+.3f}%"
    )

    print(
        f"Profit Factor  : "
        f"{perf['profit_factor']:.2f}"
        if np.isfinite(perf["profit_factor"])
        else
        f"Profit Factor  : {perf['profit_factor']}"
    )

    print(
        f"最大DD         : "
        f"{perf['max_dd']:+.2f}%"
    )

    print(
        f"Sharpe         : "
        f"{perf['sharpe']:.2f}"
        if np.isfinite(perf["sharpe"])
        else
        f"Sharpe         : {perf['sharpe']}"
    )

    print(
        f"Sortino        : "
        f"{perf['sortino']:.2f}"
        if np.isfinite(perf["sortino"])
        else
        f"Sortino        : {perf['sortino']}"
    )

    return oos, trades, perf


# ============================================================
# Buy & Hold
# ============================================================

def buy_and_hold(df):

    print_header("⚔️ STRATEGY vs BUY & HOLD")

    returns = df[
        "next_day_qqq"
    ].astype(float)

    perf = calculate_performance(
        returns,
        transaction_cost_pct=0.0
    )

    print(
        f"Buy & Hold : "
        f"{perf['return']:+.2f}%"
    )

    print(
        f"MaxDD      : "
        f"{perf['max_dd']:+.2f}%"
    )

    print(
        f"Sharpe     : "
        f"{perf['sharpe']:.2f}"
        if np.isfinite(perf["sharpe"])
        else
        f"Sharpe     : {perf['sharpe']}"
    )

    return perf


# ============================================================
# Monthly
# ============================================================

def monthly_oos(
    oos,
    strategy_name
):

    print_header("📆 MONTHLY OOS")

    trades = oos.loc[
        oos["selected"]
    ].copy()

    if len(trades) == 0:
        return pd.DataFrame()

    trades["month"] = (
        trades["date"]
        .dt.to_period("M")
        .astype(str)
    )

    rows = []

    for month, group in trades.groupby(
        "month",
        sort=True
    ):

        perf = calculate_performance(
            group["next_day_qqq"]
        )

        rows.append({
            "month": month,
            "count": len(group),
            "mean": group[
                "next_day_qqq"
            ].mean(),
            "median": group[
                "next_day_qqq"
            ].median(),
            "win_rate": perf["win_rate"],
            "return": perf["return"],
            "max_dd": perf["max_dd"],
        })

    result = pd.DataFrame(rows)

    print(
        result.round(4).to_string(
            index=False
        )
    )

    return result


# ============================================================
# Bootstrap
# ============================================================

def bootstrap_returns(
    returns,
    iterations=BOOTSTRAP_ITERATIONS,
    seed=BOOTSTRAP_SEED
):

    returns = np.asarray(
        returns,
        dtype=float
    )

    returns = returns[
        np.isfinite(returns)
    ]

    if len(returns) == 0:
        return {
            "mean": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "positive_probability": np.nan,
        }

    rng = np.random.default_rng(
        seed
    )

    simulated_returns = []

    n = len(returns)

    for _ in range(iterations):

        sample = rng.choice(
            returns,
            size=n,
            replace=True
        )

        net = (
            sample
            -
            TRANSACTION_COST_PCT
        )

        equity = (
            1
            +
            net / 100
        ).prod()

        total_return = (
            equity - 1
        ) * 100

        simulated_returns.append(
            total_return
        )

    simulated_returns = np.asarray(
        simulated_returns
    )

    return {
        "mean": simulated_returns.mean(),
        "ci_low": np.percentile(
            simulated_returns,
            2.5
        ),
        "ci_high": np.percentile(
            simulated_returns,
            97.5
        ),
        "positive_probability": (
            (
                simulated_returns > 0
            ).mean()
            * 100
        ),
    }


def run_bootstrap(trades):

    print_header("🎲 BOOTSTRAP")

    result = bootstrap_returns(
        trades["next_day_qqq"]
    )

    print(
        f"平均Bootstrap Return : "
        f"{result['mean']:+.2f}%"
    )

    print(
        f"95% CI : "
        f"{result['ci_low']:+.2f}% ～ "
        f"{result['ci_high']:+.2f}%"
    )

    print(
        f"プラス確率 : "
        f"{result['positive_probability']:.2f}%"
    )

    return result


# ============================================================
# Permutation test
# ============================================================

def permutation_test(
    df,
    strategy_name="DOWN_BOTH",
    threshold=0.50,
    iterations=PERMUTATION_ITERATIONS,
    seed=PERMUTATION_SEED
):

    print_header("🧪 PERMUTATION TEST")

    signal = create_strategy_signal(
        df,
        strategy_name,
        threshold
    )

    actual_returns = df[
        "next_day_qqq"
    ].to_numpy(
        dtype=float
    )

    actual_returns = np.nan_to_num(
        actual_returns,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    actual_selected = actual_returns[
        signal.to_numpy()
    ]

    actual_perf = calculate_performance(
        actual_selected
    )

    observed = actual_perf[
        "return"
    ]

    rng = np.random.default_rng(
        seed
    )

    simulated = []

    for _ in range(iterations):

        shuffled = rng.permutation(
            actual_returns
        )

        selected = shuffled[
            signal.to_numpy()
        ]

        perf = calculate_performance(
            selected
        )

        value = perf["return"]

        if np.isfinite(value):
            simulated.append(
                value
            )

    simulated = np.asarray(
        simulated
    )

    if len(simulated) == 0:
        p_value = np.nan

    else:
        p_value = (
            (
                simulated >= observed
            ).mean()
        )

    print(
        f"Observed Return : "
        f"{observed:+.2f}%"
    )

    print(
        f"Permutation Mean : "
        f"{simulated.mean():+.2f}%"
    )

    print(
        f"Permutation 95% CI : "
        f"{np.percentile(simulated, 2.5):+.2f}% ～ "
        f"{np.percentile(simulated, 97.5):+.2f}%"
    )

    print(
        f"p-value : "
        f"{p_value:.4f}"
    )

    if np.isfinite(p_value):

        if p_value < 0.05:
            print(
                "✅ シグナルとリターンの対応は"
                "ランダムでは説明しにくい"
            )
        else:
            print(
                "⚠️ ランダムでも同程度の結果が"
                "出る可能性があります"
            )

    return {
        "observed_return": observed,
        "permutation_mean": simulated.mean(),
        "ci_low": np.percentile(
            simulated,
            2.5
        ),
        "ci_high": np.percentile(
            simulated,
            97.5
        ),
        "p_value": p_value,
    }


# ============================================================
# Threshold Walk-forward sensitivity
# ============================================================

def threshold_walkforward():

    print_header(
        "📐 THRESHOLD WALK-FORWARD SENSITIVITY"
    )

    rows = []

    for threshold in DOWN_THRESHOLDS:

        fold_result = walk_forward_strategy(
            GLOBAL_DF,
            strategy_name="DOWN_BOTH",
            threshold=threshold
        )

        if len(fold_result) == 0:
            continue

        returns = fold_result[
            "return"
        ].astype(float)

        rows.append({
            "threshold": threshold,
            "threshold_pct": threshold * 100,
            "folds": len(fold_result),
            "total_return_sum": returns.sum(),
            "mean_fold_return": returns.mean(),
            "positive_folds": (
                returns > 0
            ).sum(),
            "positive_fold_rate": (
                returns > 0
            ).mean() * 100,
            "mean_max_dd": fold_result[
                "max_dd"
            ].mean(),
            "total_trades": fold_result[
                "trades"
            ].sum(),
        })

    result = pd.DataFrame(rows)

    print()
    print(
        result.round(4).to_string(
            index=False
        )
    )

    return result


# ============================================================
# OOS threshold comparison
# ============================================================

def oos_threshold_comparison():

    print_header(
        "🔬 OOS THRESHOLD COMPARISON"
    )

    rows = []

    for threshold in DOWN_THRESHOLDS:

        result = combined_oos(
            GLOBAL_DF,
            "DOWN_BOTH",
            threshold
        )

        if result is None:
            continue

        oos, trades, perf = result

        rows.append({
            "threshold": threshold,
            "threshold_pct": threshold * 100,
            "return": perf["return"],
            "max_dd": perf["max_dd"],
            "win_rate": perf["win_rate"],
            "trades": perf["trades"],
            "profit_factor": perf[
                "profit_factor"
            ],
            "sharpe": perf["sharpe"],
        })

    result = pd.DataFrame(rows)

    print()
    print(
        result.round(4).to_string(
            index=False
        )
    )

    return result


# ============================================================
# Stability summary
# ============================================================

def stability_summary(
    threshold_result,
    oos_result
):

    print_header("🧠 ROBUSTNESS SUMMARY")

    print()
    print(
        "Threshold sensitivity"
    )

    if len(threshold_result) > 0:

        positive = (
            threshold_result[
                "positive_fold_rate"
            ]
        )

        print(
            f"Fold positive rate range : "
            f"{positive.min():.1f}% ～ "
            f"{positive.max():.1f}%"
        )

        print(
            f"Mean fold return range : "
            f"{threshold_result['mean_fold_return'].min():+.2f}% ～ "
            f"{threshold_result['mean_fold_return'].max():+.2f}%"
        )

    print()
    print(
        "OOS threshold comparison"
    )

    if len(oos_result) > 0:

        best = oos_result.loc[
            oos_result["return"].idxmax()
        ]

        base = oos_result.loc[
            np.isclose(
                oos_result["threshold"],
                0.50
            )
        ]

        if len(base) > 0:

            base_return = base.iloc[
                0
            ]["return"]

            print(
                f"50% threshold OOS : "
                f"{base_return:+.2f}%"
            )

        print(
            f"Best sensitivity result : "
            f"{best['threshold_pct']:.1f}% "
            f"/ "
            f"{best['return']:+.2f}%"
        )

    print()
    print(
        "⚠️ 注意:"
    )

    print(
        "この表は最良閾値を採用するためのものではありません。"
    )

    print(
        "50%付近で結果が大きく崩れないかを確認する"
        "ロバストネス分析です。"
    )


# ============================================================
# Save
# ============================================================

def save_results(
    df,
    fixed_trades,
    threshold_result,
    wf_result,
    oos,
    monthly,
    bootstrap_result,
    permutation_result,
    oos_threshold_result
):

    print_header("💾 SAVE")

    # --------------------------------------------------------
    # Diagnostic
    # --------------------------------------------------------

    diagnostic = df[
        [
            "date",
            "ai_probability",
            "ml_probability",
            "ai_direction_calc",
            "ml_direction_calc",
            "direction",
            "agreement",
            "probability_gap",
            "strength",
            "next_day_qqq",
            "down_both",
            "signal",
        ]
    ].copy()

    diagnostic_file = os.path.join(
        OUTPUT_DIR,
        "signal_diagnostic_v2_17.csv"
    )

    diagnostic.to_csv(
        diagnostic_file,
        index=False
    )

    print(diagnostic_file)

    # --------------------------------------------------------
    # Fixed strategy trades
    # --------------------------------------------------------

    if fixed_trades is not None:

        fixed_file = os.path.join(
            OUTPUT_DIR,
            "signal_down_both_v2_17.csv"
        )

        fixed_trades.to_csv(
            fixed_file,
            index=False
        )

        print(fixed_file)

    # --------------------------------------------------------
    # Threshold sensitivity
    # --------------------------------------------------------

    threshold_file = os.path.join(
        OUTPUT_DIR,
        "signal_threshold_sensitivity_v2_17.csv"
    )

    threshold_result.to_csv(
        threshold_file,
        index=False
    )

    print(threshold_file)

    # --------------------------------------------------------
    # Walk-forward
    # --------------------------------------------------------

    wf_file = os.path.join(
        OUTPUT_DIR,
        "signal_walkforward_v2_17.csv"
    )

    wf_result.to_csv(
        wf_file,
        index=False
    )

    print(wf_file)

    # --------------------------------------------------------
    # OOS
    # --------------------------------------------------------

    oos_file = os.path.join(
        OUTPUT_DIR,
        "signal_oos_v2_17.csv"
    )

    oos.to_csv(
        oos_file,
        index=False
    )

    print(oos_file)

    # --------------------------------------------------------
    # Monthly
    # --------------------------------------------------------

    monthly_file = os.path.join(
        OUTPUT_DIR,
        "signal_monthly_v2_17.csv"
    )

    monthly.to_csv(
        monthly_file,
        index=False
    )

    print(monthly_file)

    # --------------------------------------------------------
    # Bootstrap
    # --------------------------------------------------------

    bootstrap_file = os.path.join(
        OUTPUT_DIR,
        "signal_bootstrap_v2_17.csv"
    )

    pd.DataFrame([
        bootstrap_result
    ]).to_csv(
        bootstrap_file,
        index=False
    )

    print(bootstrap_file)

    # --------------------------------------------------------
    # Permutation
    # --------------------------------------------------------

    permutation_file = os.path.join(
        OUTPUT_DIR,
        "signal_permutation_v2_17.csv"
    )

    pd.DataFrame([
        permutation_result
    ]).to_csv(
        permutation_file,
        index=False
    )

    print(permutation_file)

    # --------------------------------------------------------
    # OOS threshold comparison
    # --------------------------------------------------------

    oos_threshold_file = os.path.join(
        OUTPUT_DIR,
        "signal_oos_threshold_v2_17.csv"
    )

    oos_threshold_result.to_csv(
        oos_threshold_file,
        index=False
    )

    print(oos_threshold_file)


# ============================================================
# MAIN
# ============================================================

GLOBAL_DF = None


def main():

    global GLOBAL_DF

    print("=" * 70)
    print("🤖 PayPay AI Signal Analysis v2.17")
    print("=" * 70)

    print(
        "Fixed DOWN_BOTH Robustness"
    )

    print(
        "Threshold Sensitivity"
    )

    print(
        "Walk-Forward Stability"
    )

    print(
        "Bootstrap Robustness"
    )

    print(
        "Permutation Test"
    )

    print(
        "No Full-Sample Optimization"
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_data()

    GLOBAL_DF = df.copy()

    # --------------------------------------------------------
    # Signals
    # --------------------------------------------------------

    df = calculate_signals(
        df
    )

    # --------------------------------------------------------
    # Integrity
    # --------------------------------------------------------

    signal_integrity(
        df
    )

    # --------------------------------------------------------
    # Fixed strategy
    # --------------------------------------------------------

    fixed_result = evaluate_fixed_strategy(
        df
    )

    if fixed_result is None:
        fixed_trades = pd.DataFrame()
        fixed_perf = None

    else:
        fixed_trades, fixed_perf = (
            fixed_result
        )

    # --------------------------------------------------------
    # Threshold sensitivity
    # --------------------------------------------------------

    threshold_result = (
        threshold_sensitivity(
            df
        )
    )

    # --------------------------------------------------------
    # Walk-forward
    # --------------------------------------------------------

    wf_result = (
        walk_forward_strategy(
            df,
            strategy_name="DOWN_BOTH",
            threshold=0.50
        )
    )

    # --------------------------------------------------------
    # OOS
    # --------------------------------------------------------

    oos_result = combined_oos(
        df,
        strategy_name="DOWN_BOTH",
        threshold=0.50
    )

    if oos_result is None:
        raise RuntimeError(
            "OOS result could not be created."
        )

    oos, oos_trades, oos_perf = (
        oos_result
    )

    # --------------------------------------------------------
    # Buy & Hold
    # --------------------------------------------------------

    buy_hold_perf = buy_and_hold(
        df
    )

    print()
    print(
        f"Strategy   : "
        f"{oos_perf['return']:+.2f}%"
    )

    print(
        f"Buy & Hold : "
        f"{buy_hold_perf['return']:+.2f}%"
    )

    print(
        f"Difference  : "
        f"{oos_perf['return'] - buy_hold_perf['return']:+.2f}pt"
    )

    print()
    print(
        f"Strategy MaxDD   : "
        f"{oos_perf['max_dd']:+.2f}%"
    )

    print(
        f"Buy & Hold MaxDD : "
        f"{buy_hold_perf['max_dd']:+.2f}%"
    )

    # --------------------------------------------------------
    # Monthly
    # --------------------------------------------------------

    monthly = monthly_oos(
        oos,
        "DOWN_BOTH"
    )

    # --------------------------------------------------------
    # Bootstrap
    # --------------------------------------------------------

    bootstrap_result = run_bootstrap(
        oos_trades
    )

    # --------------------------------------------------------
    # Permutation
    # --------------------------------------------------------

    permutation_result = (
        permutation_test(
            df,
            strategy_name="DOWN_BOTH",
            threshold=0.50
        )
    )

    # --------------------------------------------------------
    # Threshold walk-forward
    # --------------------------------------------------------

    threshold_wf_result = (
        threshold_walkforward()
    )

    # --------------------------------------------------------
    # OOS threshold comparison
    # --------------------------------------------------------

    oos_threshold_result = (
        oos_threshold_comparison()
    )

    # --------------------------------------------------------
    # Robustness summary
    # --------------------------------------------------------

    stability_summary(
        threshold_wf_result,
        oos_threshold_result
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_results(
        df=df,
        fixed_trades=fixed_trades,
        threshold_result=threshold_result,
        wf_result=wf_result,
        oos=oos,
        monthly=monthly,
        bootstrap_result=bootstrap_result,
        permutation_result=permutation_result,
        oos_threshold_result=oos_threshold_result,
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("🏁 v2.17 COMPLETE")
    print("=" * 70)

    print(
        "目的 : "
        "v2.16で発見されたDOWN_BOTH構造の"
        "ロバストネス検証"
    )

    print()
    print(
        "検証項目:"
    )

    print(
        "1. 固定DOWN_BOTH"
    )

    print(
        "2. 45～55% threshold sensitivity"
    )

    print(
        "3. Walk-Forward stability"
    )

    print(
        "4. Bootstrap"
    )

    print(
        "5. Permutation test"
    )

    print()
    print(
        "⚠️ このバージョンでは"
        "全期間から最適閾値を選択していません。"
    )

    print(
        "次の判断材料:"
    )

    print(
        "・DOWN_BOTHが50%付近で安定しているか"
    )

    print(
        "・Foldを跨いでもプラスが続くか"
    )

    print(
        "・Permutationで偶然ではないか"
    )

    print(
        "・Bootstrap CIが0を跨ぐか"
    )


if __name__ == "__main__":
    main()