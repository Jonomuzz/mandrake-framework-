print("🔥🔥🔥 THIS IS CORE/DATA.PY V3 ACTIVE 🔥🔥🔥")
import requests
import pandas as pd

BASE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol, interval="1m", limit=100):
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&limit={limit}"

    response = requests.get(url, timeout=10)
    data = response.json()

    if not isinstance(data, list):
        raise Exception(f"Bad response for {symbol}: {data}")

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    # force numeric conversion safely
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
