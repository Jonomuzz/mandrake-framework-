import time
import requests
from collections import defaultdict

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

# IMPORTANT: replace these with REAL values in Railway env OR hardcode for testing
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BASE_URL = "https://api.binance.com/api/v3/klines"

# Store previous MA state per symbol
state = defaultdict(lambda: {
    "prev_ma5": None,
    "prev_ma20": None
})

# ----------------------------
# TELEGRAM (FIXED - DEBUG SAFE)
# ----------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Telegram not configured (missing token/chat_id)")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        r = requests.post(url, data=payload, timeout=10)

        print("📨 Telegram status:", r.status_code)
        print("📨 Telegram response:", r.text)

        if r.status_code != 200:
            print("❌ Telegram failed — check token/chat_id")

    except Exception as e:
        print("❌ Telegram exception:", e)


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

    closes = [float(candle[4]) for candle in data]
    return closes


def sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


# ----------------------------
# STRATEGY
# ----------------------------
def get_signal(symbol, closes):
    ma5 = sma(closes, 5)
    ma20 = sma(closes, 20)

    if ma5 is None or ma20 is None:
        return None

    prev_ma5 = state[symbol]["prev_ma5"]
    prev_ma20 = state[symbol]["prev_ma20"]

    # Need previous values to detect crossover
    if prev_ma5 is None or prev_ma20 is None:
        state[symbol]["prev_ma5"] = ma5
        state[symbol]["prev_ma20"] = ma20
        return None

    signal = None

    # CROSS UP → BUY
    if prev_ma5 <= prev_ma20 and ma5 > ma20:
        signal = "BUY"

    # CROSS DOWN → SELL
    elif prev_ma5 >= prev_ma20 and ma5 < ma20:
        signal = "SELL"

    # update state AFTER logic
    state[symbol]["prev_ma5"] = ma5
    state[symbol]["prev_ma20"] = ma20

    return signal


# ----------------------------
# MAIN LOOP
# ----------------------------
def run_bot():
    print("🤖 Bot started")

    send_telegram("🤖 BOT STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                print(f"Checking {symbol}...")

                closes = get_klines(symbol)
                signal = get_signal(symbol, closes)

                print(f"{symbol} signal:", signal)

                if signal:
                    msg = f"📊 {symbol} SIGNAL: {signal}"
                    print("📨 SENDING:", msg)
                    send_telegram(msg)

            except Exception as e:
                print(f"Error on {symbol}:", e)

        print("Cycle complete. Sleeping...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
