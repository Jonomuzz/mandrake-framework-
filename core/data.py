print("🔥 FILE LOADED - TOP LEVEL EXECUTION CONFIRMED")

import requests
import pandas as pd

print("🔥 PANDAS IMPORT SUCCESSFUL")


BASE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol, interval="1m", limit=100):
    print("🔥 GET_KLINES CALLED FOR:", symbol)

    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&limit={limit}"

    response = requests.get(url, timeout=10)
    data = response.json()

    print("🔥 DATA RECEIVED OK")

    df = pd.DataFrame(data)

    print("🔥 DATAFRAME CREATED")

    return df
