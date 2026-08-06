import yfinance as yf
import requests

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
    
    # ゴールド前日比
    gold_change = (
        (gold_hist["Close"].iloc[-1] - gold_hist["Close"].iloc[-2])
        / gold_hist["Close"].iloc[-2]
        * 100
    )

    # 米10年金利
    tnx_value = float(tnx_hist["Close"].iloc[-1])

    # ドル円
    usdjpy_value = float(usdjpy_hist["Close"].iloc[-1])
    
    qqq_hist["MA25"] = qqq_hist["Close"].rolling(25).mean()
    qqq_hist["MA75"] = qqq_hist["Close"].rolling(75).mean()
    
    change = (
    (qqq_hist["Close"].iloc[-1] - qqq_hist["Close"].iloc[-2])
    / qqq_hist["Close"].iloc[-2]
    * 100
)

    spy_change = (
        (spy_hist["Close"].iloc[-1] - spy_hist["Close"].iloc[-2])
        / spy_hist["Close"].iloc[-2]
        * 100
    )

    vix_value = float(vix_hist["Close"].iloc[-1])

    ma25 = float(qqq_hist["MA25"].iloc[-1])
    ma75 = float(qqq_hist["MA75"].iloc[-1])

    fear_greed = get_fear_greed()


    return {
        "change": change,
        "spy_change": spy_change,
        "vix": vix_value,
        "ma25": ma25,
        "ma75": ma75,
        "fear_greed": fear_greed,
        "gold_change": gold_change,
        "tnx": tnx_value,
        "usdjpy": usdjpy_value,
    }
    
def get_fear_greed():

    try:

        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

        r = requests.get(url, timeout=10)

        data = r.json()

        return int(data["fear_and_greed"]["score"])

    except Exception as e:

        print("Fear&Greed取得失敗", e)

        return 50