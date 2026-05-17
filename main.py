import time
import os
import pandas as pd
import requests

from core.strategy_registry import get_strategy
from core.position_manager import init
from core.execution import execute
from core.portfolio import portfolio

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100

BASE_URL = "https://api.binance.com/api/v3/klines"


def get_klines(symbol):
    r = requests.get(BASE_URL, params={
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    })

    data = r.json()

    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)

    return df


def run():
    print("🚀 OPTION B ENGINE STARTED")

    init(SYMBOLS)

    while True:
        for symbol in SYMBOLS:

            df = get_klines(symbol)

            # -------------------------
            # SIMPLE STRATEGY PICK
            # -------------------------
            strategy = "mean_reversion"
            strat = get_strategy(strategy)

            df = strat.calculate_indicators(df)
            signal = strat.check_signal(df)

            price = df["close"].iloc[-1]

            print(f"{symbol} | {strategy} | {signal}")

            if signal:
                execute(symbol, signal, price)

        print("Cycle complete...\n")
        time.sleep(60)


if __name__ == "__main__":
    run()
