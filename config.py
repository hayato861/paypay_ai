import os

try:
    # ローカル開発用
    from config_local import *
except ImportError:
    # GitHub Actions用
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    X_API_KEY = os.getenv("X_API_KEY")
    X_API_SECRET = os.getenv("X_API_SECRET")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")