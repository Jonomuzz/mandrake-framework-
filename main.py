import time
import os
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_ma_crossover,
    breakout,
    momentum,
    kst
)

from core.config import PAIRS, SLEEP, ACTIVE_STRATEGY
from core.execution import handle_trade, initialize_pairs
from core.metrics import evaluate_strategies, get_leaderboard, strategy_stats
from core.telegram import send_telegram

BASE_URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1m"
LIMIT = 100


def get_klines(symbol):
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)
    return df


def select_strategy(df):
    ma20 = df["close"].rolling(20).mean()
    slope = ma20.diff().iloc[-1]
    vol = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    if abs(slope) > vol * 0.15:
        return "trend_ma_crossover"

    if vol_ratio > 0.01:
        return "breakout"

    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


def get_signal(df, strategy):

    if strategy == "trend_ma_crossover":
        df = trend_ma_crossover.calculate_indicators(df)
        return trend_ma_crossover.check_signal(df)

    if strategy == "mean_reversion":
        df = mean_reversion.calculate_indicators(df)
        return mean_reversion.check_signal(df)

    if strategy == "breakout":
        df = breakout.calculate_indicators(df)
        return breakout.check_signal(df)

    if strategy == "momentum":
        df = momentum.calculate_indicators(df)
        return momentum.check_signal(df)

    return None


def run():
    print("🚀 SWITCHER ENGINE STARTED")
    send_telegram("🚀 SWITCHER ENGINE STARTED")

    initialize_pairs(PAIRS)

    while True:

        for symbol in PAIRS:

            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)

                if strategy_stats.get(strategy, {}).get("disabled"):
                    continue

                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                print(f"[{symbol}] {strategy} => {signal}")

                if signal:
                    handle_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        evaluate_strategies()

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
