import time
import requests
import os
from collections import defaultdict
import pandas as pd

from strategies import mean_reversion, trend, breakout, momentum

# ----------------------------
# CONFIG
# ----------------------------
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
CANDLE_LIMIT = 50
BASE_URL = "https://api.binance.com/api/v3/klines"

# ----------------------------
# ENV VARIABLES
# ----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BOT_NAME = os.getenv("BOT_NAME", "mandrake-bot")
ACTIVE_STRATEGY = os.getenv("ACTIVE_STRATEGY", "trend")

# ----------------------------
# STATE
# ----------------------------
state = defaultdict(dict)

# ----------------------------
# TELEGRAM
# ----------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ----------------------------
# DATA
# ----------------------------
def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": CANDLE_LIMIT
    }

    r = requests.get(BASE_URL, params=params, timeout=10)
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df

# ----------------------------
# STRATEGY ROUTER
# ----------------------------
def get_signal(df):
    global ACTIVE_STRATEGY

    if ACTIVE_STRATEGY == "mean_reversion":
        df = mean_reversion.calculate_indicators(df)
        return mean_reversion.check_signal(df)

    elif ACTIVE_STRATEGY == "trend":
        df = trend.calculate_indicators(df)
        return trend.check_signal(df)

    elif ACTIVE_STRATEGY == "breakout":
        df = breakout.calculate_indicators(df)
        return breakout.check_signal(df)

    elif ACTIVE_STRATEGY == "momentum":
        df = momentum.calculate_indicators(df)
        return momentum.check_signal(df)

    return None

# ----------------------------
# MAIN LOOP
# ----------------------------
def run_bot():
    print(f"🤖 Bot started: {BOT_NAME} | Strategy: {ACTIVE_STRATEGY}")

    send_telegram(f"🤖 {BOT_NAME} STARTED | Strategy: {ACTIVE_STRATEGY}")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_klines(symbol)
                signal = get_signal(df)

                print(f"{symbol} | {ACTIVE_STRATEGY} | signal:", signal)

                if signal:
                    # ✅ DEBUG LINE ADDED HERE (CRITICAL TEST)
                    msg = f"📊 {BOT_NAME} | STRATEGY={ACTIVE_STRATEGY} | {symbol} SIGNAL: {signal}"
                    send_telegram(msg)

            except Exception as e:
                print(f"Error {symbol}:", e)

        print("Cycle complete. Sleeping...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
