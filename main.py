import time
import os
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)

from core.signal_strength import score_signal
from core.frequency_controller import FrequencyController
from core.telegram_commands import process_command, frequency_state
from core.notifications import send_telegram
from core.config import PAIRS, INTERVAL, LIMIT, SLEEP

# =========================
# INIT
# =========================
freq_controller = FrequencyController()

BASE_URL = "https://api.binance.com/api/v3/klines"


# =========================
# DATA
# =========================
def get_klines(symbol):
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)
    return df


# =========================
# REGIME DETECTION
# =========================
def select_strategy(df):
    ma20 = df["close"].rolling(20).mean()
    slope = ma20.diff().iloc[-1]
    vol = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    if abs(slope) > vol * 0.15:
        return "trend"

    if vol_ratio > 0.01:
        return "breakout"

    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


# =========================
# ROUTER
# =========================
def get_signal(df, strategy):

    if strategy == "trend":
        df = trend_strength_crossover.calculate_indicators(df)
        return trend_strength_crossover.check_signal(df)

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


# =========================
# MAIN LOOP
# =========================
def run():
    print("🚀 FULL TRADING BRAIN STARTED")
    send_telegram("🚀 FULL TRADING BRAIN STARTED")

    while True:
        for symbol in PAIRS:
            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)
                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                print(f"{symbol} | {strategy} | {signal}")

                # =========================
                # PAUSE CHECK
                # =========================
                if frequency_state.get("paused"):
                    continue

                if signal:
                    score = score_signal(df, strategy)

                    print(f"{symbol} | SCORE {score}")

                    # ONLY HIGH QUALITY TRADES
                    if score >= 70 and freq_controller.can_trade(symbol):

                        msg = f"{symbol} | {strategy.upper()} | {signal} @ {price} | SCORE {score}"
                        send_telegram(msg)

                        freq_controller.mark_trade(symbol)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
