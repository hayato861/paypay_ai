from pathlib import Path

import pandas as pd


BULLISH_COURSES = {
    "テクノロジー",
    "テクノロジーチャレンジ",
    "チャレンジ",
    "スタンダード",
}

MINIMUM_TEST_SAMPLES = 200
MINIMUM_EDGE = 0.02


def directional_accuracy(actual, prediction):
    actual = pd.Series(actual).astype(int)
    prediction = pd.Series(prediction).astype(int)

    if len(actual) == 0 or len(actual) != len(prediction):
        raise ValueError("actualとpredictionは同じ長さの非空データが必要です")

    return float((actual.to_numpy() == prediction.to_numpy()).mean())


def majority_baseline(actual):
    actual = pd.Series(actual).astype(int)

    if len(actual) == 0:
        raise ValueError("actualは非空データが必要です")

    return float(actual.value_counts(normalize=True).max())


def recommendation_prediction(courses):
    return pd.Series(courses).isin(BULLISH_COURSES).astype(int)


def evaluate_predictions(actual, prediction):
    accuracy = directional_accuracy(actual, prediction)
    baseline = majority_baseline(actual)

    return {
        "samples": len(actual),
        "accuracy": accuracy,
        "baseline": baseline,
        "edge": accuracy - baseline,
    }


def passes_adoption_gate(
    result,
    minimum_samples=MINIMUM_TEST_SAMPLES,
    minimum_edge=MINIMUM_EDGE,
):
    return (
        result["samples"] >= minimum_samples
        and result["edge"] >= minimum_edge
    )


def evaluate_backtest(path=Path("data/backtest.csv"), test_fraction=0.2):
    df = pd.read_csv(path)
    required = {"date", "recommend", "next_day_qqq"}
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(f"backtest列不足: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    df["next_day_qqq"] = pd.to_numeric(df["next_day_qqq"], errors="coerce")
    df = df.dropna(subset=["date", "recommend", "next_day_qqq"])
    df = df[df["next_day_qqq"] != 0].sort_values("date").reset_index(drop=True)

    split = int(len(df) * (1 - test_fraction))
    test = df.iloc[split:].copy()
    actual = (test["next_day_qqq"] > 0).astype(int)
    prediction = recommendation_prediction(test["recommend"])

    return evaluate_predictions(actual, prediction)


def evaluate_ml(path, probability_column=None):
    df = pd.read_csv(path)
    required = {"next_day_qqq", "prediction"}
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(f"ML結果列不足: {sorted(missing)}")

    df["next_day_qqq"] = pd.to_numeric(df["next_day_qqq"], errors="coerce")
    df["prediction"] = pd.to_numeric(df["prediction"], errors="coerce")
    df = df.dropna(subset=["next_day_qqq", "prediction"])
    df = df[df["next_day_qqq"] != 0]

    if probability_column:
        df[probability_column] = pd.to_numeric(df[probability_column], errors="coerce")
        df = df.dropna(subset=[probability_column])

    actual = (df["next_day_qqq"] > 0).astype(int)
    return evaluate_predictions(actual, df["prediction"].astype(int))


def print_result(name, result):
    decision = "ADOPT" if passes_adoption_gate(result) else "REJECT"
    print(
        f"{name}: n={result['samples']}, "
        f"accuracy={result['accuracy']:.1%}, "
        f"baseline={result['baseline']:.1%}, "
        f"edge={result['edge']:+.1%}, "
        f"decision={decision}"
    )


def run():
    print_result("course/test", evaluate_backtest())
    print_result("ml/v1", evaluate_ml("data/ml_test.csv", "probability_up"))
    print_result("ml/v2", evaluate_ml("data/ml_test_v2.csv", "up_probability"))


if __name__ == "__main__":
    run()
