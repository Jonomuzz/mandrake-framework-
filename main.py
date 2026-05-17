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

# ================= CONFIG =================
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100
SLEEP = 60

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BASE_URL = "https://api.binance.com/api/v3/klines"


# ================= TELEGRAM =================
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ================= DATA =================
def get_klines(symbol):
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)
    return df


# ================= REGIME DETECTOR (FIXED + EXPOSED) =================
def select_strategy(df):
    ma20 = df["close"].rolling(20).mean()
    slope = ma20.diff().iloc[-1]
    vol = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    # DEBUG OUTPUT (IMPORTANT)
    print(f"[REGIME DEBUG] Slope={slope:.6f} Vol={vol:.6f} Ratio={vol_ratio:.6f}")

    # TREND (RELAXED THRESHOLD - FIX)
    if abs(slope) > vol * 0.05:
        return "trend"

    # BREAKOUT
    if vol_ratio > 0.01:
        return "breakout"

    # MOMENTUM
    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


# ================= ROUTER =================
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


# ================= MAIN LOOP =================
def run():
    print("🚀 SWITCHER ENGINE STARTED")
    send_telegram("🚀 SWITCHER ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)
                signal = get_signal(df, strategy)

                price = df["close"].iloc[-1]

                print(f"{symbol} | {strategy} | {signal} | {price}")

                if signal:
                    msg = f"{symbol} | {strategy.upper()} | {signal} @ {price}"
                    send_telegram(msg)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
