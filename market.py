import yfinance as yf

TICKERS = {
    "QQQ": "QQQ",
    "SPY": "SPY",
    "VIX": "^VIX",
    "GLD": "GLD",
    "TNX": "^TNX",
    "USDJPY": "JPY=X",
}


def get_market_data():
    qqq = yf.Ticker(TICKERS["QQQ"])
    spy = yf.Ticker(TICKERS["SPY"])
    vix = yf.Ticker(TICKERS["VIX"])
    gold = yf.Ticker(TICKERS["GLD"])
    tnx = yf.Ticker(TICKERS["TNX"])
    usdjpy = yf.Ticker(TICKERS["USDJPY"])

    qqq_hist = qqq.history(period="120d")
    spy_hist = spy.history(period="5d")
    vix_hist = vix.history(period="5d")
    gold_hist = gold.history(period="5d")
    tnx_hist = tnx.history(period="5d")
    usdjpy_hist = usdjpy.history(period="5d")
    

    qqq_hist["MA25"] = qqq_hist["Close"].rolling(25).mean()
    qqq_hist["MA75"] = qqq_hist["Close"].rolling(75).mean()

    return {
        "price": qqq_hist["Close"].iloc[-1],
        "change": (
            (qqq_hist["Close"].iloc[-1] - qqq_hist["Close"].iloc[-2])
            / qqq_hist["Close"].iloc[-2]
            * 100
        ),
        "spy_change": (
            (spy_hist["Close"].iloc[-1] - spy_hist["Close"].iloc[-2])
            / spy_hist["Close"].iloc[-2]
            * 100
        ),
        "vix": vix_hist["Close"].iloc[-1],
        "gold": gold_hist["Close"].iloc[-1],
        "ma25": qqq_hist["MA25"].iloc[-1],
        "tnx": tnx_hist["Close"].iloc[-1],
        "usdjpy": usdjpy_hist["Close"].iloc[-1],
        "ma75": qqq_hist["MA75"].iloc[-1],
    }