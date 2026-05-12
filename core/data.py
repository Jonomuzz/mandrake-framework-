import requests
import pandas as pd

from core.config import INTERVAL, LIMIT


def get_klines(symbol):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    return df
