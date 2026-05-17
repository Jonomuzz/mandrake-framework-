import requests
import pandas as pd

BASE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol, interval="1m", limit=100):
    """
    Fetch OHLCV data from Binance and return clean dataframe.
    """

    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url, timeout=10)
    data = response.json()

    if not isinstance(data, list):
        raise Exception(f"Invalid API response for {symbol}: {data}")

    df = pd.DataFrame(data, columns=[
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "num_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore"
    ])

    # enforce numeric types (critical for indicators)
    numeric_cols = ["open", "high", "low", "close", "volume"]

    for col in numeric_cols:
        df[col] = df[col].astype(float)

    return df
