import time
import requests
import pandas as pd
import os

from core.config import PAIRS, SLEEP
from core.execution import handle_trade, initialize_pairs
from core.telegram import send_telegram


# =========================
# BINANCE CONFIG
# =========================
BASE_URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1m"
LIMIT = 100


# =========================
# DATA FETCH
# =========================
def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    r = requests.get(BASE_URL, params=params, timeout=10)
    data = r.json()

    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)

    return df


# =========================
# STRATEGY SELECTOR (NO REGIME ENGINE)
# =========================
def select_strategy(df):
    ma20 = df["close"].rolling(20).mean()
    slope = ma20.diff().iloc[-1]
    vol = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    # TREND
    if abs(slope) > vol * 0.15:
        return "trend_strength_crossover"

    # BREAKOUT
    if vol_ratio > 0.01:
        return "breakout"

    # MOMENTUM
    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    # DEFAULT
    return "mean_reversion"


# =========================
# SIGNAL ENGINE (REGISTRY)
# =========================
def get_signal(df, strategy_name):

    if strategy_name == "mean_reversion":
        from strategies import mean_reversion
        df = mean_reversion.calculate_indicators(df)
        return mean_reversion.check_signal(df)

    if strategy_name == "breakout":
        from strategies import breakout
        df = breakout.calculate_indicators(df)
        return breakout.check_signal(df)

    if strategy_name == "momentum":
        from strategies import momentum
        df = momentum.calculate_indicators(df)
        return momentum.check_signal(df)

    if strategy_name == "kst":
        from strategies import kst
        df = kst.calculate_indicators(df)
        return kst.check_signal(df)

    if strategy_name == "trend_strength_crossover":
        from strategies import trend_strength_crossover
        df = trend_strength_crossover.calculate_indicators(df)
        return trend_strength_crossover.check_signal(df)

    return None

# =========================
# MAIN LOOP
# =========================
def run():
    print("🚀 STRATEGY REGISTRY ENGINE STARTED")
    send_telegram("🚀 STRATEGY REGISTRY ENGINE STARTED")

    initialize_pairs(PAIRS)

    while True:

        for symbol in PAIRS:

            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)
                signal = get_signal(df, strategy)

                price = df["close"].iloc[-1]

                print(f"[{symbol}] Strategy={strategy} Signal={signal} Price={price}")

                if signal:
                    msg = f"{symbol} | {strategy.upper()} | {signal} @ {price}"
                    send_telegram(msg)

                    handle_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
