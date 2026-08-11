import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from backtest import load_market_history


# ============================================================
# 特徴量作成
# ============================================================

def create_features(df):

    data = df.copy()

    # --------------------------------------------------------
    # 1日変化率
    # --------------------------------------------------------

    data["qqq_1d"] = data["QQQ"].pct_change() * 100
    data["spy_1d"] = data["SPY"].pct_change() * 100
    data["vix_1d"] = data["VIX"].pct_change() * 100
    data["gold_1d"] = data["GLD"].pct_change() * 100
    data["tnx_1d"] = data["TNX"].pct_change() * 100
    data["usdjpy_1d"] = data["USDJPY"].pct_change() * 100

    # --------------------------------------------------------
    # QQQ 過去リターン
    # --------------------------------------------------------

    data["qqq_3d"] = data["QQQ"].pct_change(3) * 100
    data["qqq_5d"] = data["QQQ"].pct_change(5) * 100
    data["qqq_20d"] = data["QQQ"].pct_change(20) * 100

    # --------------------------------------------------------
    # S&P500 過去リターン
    # --------------------------------------------------------

    data["spy_3d"] = data["SPY"].pct_change(3) * 100
    data["spy_5d"] = data["SPY"].pct_change(5) * 100
    data["spy_20d"] = data["SPY"].pct_change(20) * 100

    # --------------------------------------------------------
    # VIX
    # --------------------------------------------------------

    data["vix_3d"] = data["VIX"].pct_change(3) * 100
    data["vix_5d"] = data["VIX"].pct_change(5) * 100

    # --------------------------------------------------------
    # 移動平均
    # --------------------------------------------------------

    data["qqq_ma5"] = data["QQQ"].rolling(5).mean()
    data["qqq_ma20"] = data["QQQ"].rolling(20).mean()
    data["qqq_ma50"] = data["QQQ"].rolling(50).mean()

    # --------------------------------------------------------
    # QQQの移動平均乖離率
    # --------------------------------------------------------

    data["qqq_ma5_diff"] = (
        (data["QQQ"] / data["qqq_ma5"]) - 1
    ) * 100

    data["qqq_ma20_diff"] = (
        (data["QQQ"] / data["qqq_ma20"]) - 1
    ) * 100

    data["qqq_ma50_diff"] = (
        (data["QQQ"] / data["qqq_ma50"]) - 1
    ) * 100

    # --------------------------------------------------------
    # 翌日のQQQ
    # --------------------------------------------------------

    data["next_day_qqq"] = (
        data["QQQ"].shift(-1) / data["QQQ"] - 1
    ) * 100

    # --------------------------------------------------------
    # 正解ラベル
    #
    # 上昇 = 1
    # 下落 = 0
    # --------------------------------------------------------

    data["target"] = (
        data["next_day_qqq"] > 0
    ).astype(int)

    return data


# ============================================================
# ML実行
# ============================================================

def run_ml():

    print()
    print("=" * 60)
    print("🤖 PayPay AI Machine Learning v2")
    print("=" * 60)

    # --------------------------------------------------------
    # データ取得
    # --------------------------------------------------------

    df = load_market_history("5y")

    data = create_features(df)

    # --------------------------------------------------------
    # 使用する特徴量
    # --------------------------------------------------------

    features = [

        # 基本
        "qqq_1d",
        "spy_1d",
        "vix_1d",
        "gold_1d",
        "tnx_1d",
        "usdjpy_1d",

        # 短期
        "qqq_3d",
        "qqq_5d",
        "spy_3d",
        "spy_5d",

        # 中期
        "qqq_20d",
        "spy_20d",

        # VIX
        "vix_3d",
        "vix_5d",

        # MA
        "qqq_ma5_diff",
        "qqq_ma20_diff",
        "qqq_ma50_diff",
    ]

    # 必要な列だけ残す
    model_data = data[
        features +
        [
            "target",
            "next_day_qqq"
        ]
    ].dropna()

    print()
    print("特徴量:")
    for feature in features:
        print(" ", feature)

    print()
    print("データ件数:", len(model_data))

    # --------------------------------------------------------
    # Train / Test
    #
    # 時系列なので未来のデータをTrainに混ぜない
    # --------------------------------------------------------

    split = int(len(model_data) * 0.8)

    train = model_data.iloc[:split]
    test = model_data.iloc[split:]

    X_train = train[features]
    y_train = train["target"]

    X_test = test[features]
    y_test = test["target"]

    print()
    print("📚 Train")
    print(
        train.index[0].date(),
        "～",
        train.index[-1].date()
    )
    print("件数:", len(train))

    print()
    print("🧪 Test")
    print(
        test.index[0].date(),
        "～",
        test.index[-1].date()
    )
    print("件数:", len(test))

    # --------------------------------------------------------
    # モデル
    # --------------------------------------------------------

    print()
    print("🤖 モデル学習開始")

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=6,
        min_samples_leaf=8,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    print("✅ 学習完了")

    # --------------------------------------------------------
    # 予測
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )

    # クラス1 = QQQ Up
    up_probability = probabilities[:, 1]

    # --------------------------------------------------------
    # 結果
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print()
    print("=" * 60)
    print("📊 TEST RESULT")
    print("=" * 60)

    print(
        f"Accuracy : {accuracy:.2%}"
    )

    print()

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "QQQ Down",
                "QQQ Up"
            ]
        )
    )

    # --------------------------------------------------------
    # 混同行列
    # --------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        predictions
    )

    print("Confusion Matrix")
    print(cm)

    # --------------------------------------------------------
    # Test結果DataFrame
    # --------------------------------------------------------

    result = test[
        ["next_day_qqq"]
    ].copy()

    result["actual"] = y_test.values
    result["prediction"] = predictions
    result["up_probability"] = up_probability

    result["correct"] = (
        result["actual"] ==
        result["prediction"]
    )

    # --------------------------------------------------------
    # 確率から行動を作る
    # --------------------------------------------------------

    def action(probability):

        if probability >= 0.65:
            return "強気"

        elif probability >= 0.60:
            return "やや強気"

        elif probability >= 0.55:
            return "中立"

        elif probability >= 0.45:
            return "様子見"

        elif probability >= 0.40:
            return "やや弱気"

        else:
            return "弱気"

    result["action"] = [
        action(x)
        for x in up_probability
    ]

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    output = "data/ml_test_v2.csv"

    result.to_csv(
        output,
        encoding="utf-8-sig"
    )

    print()
    print(
        "💾 保存しました:",
        output
    )

    # ========================================================
    # 確率別バックテスト
    # ========================================================

    print()
    print("=" * 60)
    print("🎯 Probability Threshold Analysis")
    print("=" * 60)

    for threshold in [
        0.50,
        0.55,
        0.60,
        0.65,
        0.70
    ]:

        selected = result[
            result["up_probability"] >= threshold
        ]

        if len(selected) == 0:
            continue

        win_rate = (
            selected["actual"].mean()
        )

        avg_return = (
            selected["next_day_qqq"].mean()
        )

        print(
            f"上昇確率 >= {threshold:.0%} "
            f"{len(selected):4d}回 "
            f"勝率 {win_rate:.1%} "
            f"平均QQQ {avg_return:+.2f}%"
        )

    # ========================================================
    # Feature Importance
    # ========================================================

    print()
    print("=" * 60)
    print("🔬 Feature Importance")
    print("=" * 60)

    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print(
        importance.to_string(
            index=False
        )
    )

    importance.to_csv(
        "data/ml_feature_importance_v2.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        "💾 保存しました: "
        "data/ml_feature_importance_v2.csv"
    )

    # --------------------------------------------------------
    # 最新予測
    # --------------------------------------------------------

    latest = model_data.iloc[-1:]

    latest_probability = model.predict_proba(
        latest[features]
    )[0][1]

    print()
    print("=" * 60)
    print("🔮 最新予測")
    print("=" * 60)

    print(
        f"QQQ上昇確率 : "
        f"{latest_probability:.1%}"
    )

    print(
        f"QQQ下落確率 : "
        f"{1 - latest_probability:.1%}"
    )

    print(
        "判定:",
        action(latest_probability)
    )


if __name__ == "__main__":
    run_ml()