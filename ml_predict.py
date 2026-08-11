import pandas as pd
from sklearn.ensemble import RandomForestClassifier


FEATURES = [
    "qqq_1d",
    "spy_1d",
    "vix_1d",
    "gold_1d",
    "tnx_1d",
    "usdjpy_1d",

    "qqq_3d",
    "qqq_5d",

    "spy_3d",
    "spy_5d",

    "qqq_20d",
    "spy_20d",

    "vix_3d",
    "vix_5d",

    "qqq_ma5_diff",
    "qqq_ma20_diff",
    "qqq_ma50_diff",
]


def train_model(df):

    df = df.dropna(
        subset=FEATURES + ["target"]
    ).copy()

    train_size = int(
        len(df) * 0.8
    )

    train = df.iloc[:train_size]

    X_train = train[FEATURES]
    y_train = train["target"]

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=10,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    return model


def predict_latest(model, df):

    latest = df.iloc[-1]

    X = latest[FEATURES].to_frame().T

    probability = model.predict_proba(X)[0]

    # target=1 が QQQ上昇
    up_probability = probability[1]

    return up_probability