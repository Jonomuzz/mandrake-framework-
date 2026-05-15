import time
import requests
from collections import defaultdict

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
CANDLE_LIMIT = 50

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

BASE_URL = "https://api.binance.com/api/v3/klines"

# Store previous MA state per symbol
state = defaultdict(lambda: {
    "prev_ma5": None,
    "prev_ma20": None
})


# ----------------------------
# TELEGRAM
# ----------------------------
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
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

    closes = [float(candle[4]) for candle in data]
    return closes


def sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


# ----------------------------
# STRATEGY (FIXED CROSSOVER)
# ----------------------------
def get_signal(symbol, closes):
    ma5 = sma(closes, 5)
    ma20 = sma(closes, 20)

    if ma5 is None or ma20 is None:
        return None

    prev = state[symbol]

    prev_ma5 = prev["prev_ma5"]
    prev_ma20 = prev["prev_ma20"]

    # update stored state AFTER checking
    state[symbol]["prev_ma5"] = ma5
    state[symbol]["prev_ma20"] = ma20

    # Need previous values to detect crossover
    if prev_ma5 is None or prev_ma20 is None:
        return None

    # CROSS UP → BUY SIGNAL
    if prev_ma5 <= prev_ma20 and ma5 > ma20:
        return "BUY"

    # CROSS DOWN → SELL SIGNAL
    if prev_ma5 >= prev_ma20 and ma5 < ma20:
        return "SELL"

    return None


# ----------------------------
# MAIN LOOP
# ----------------------------
def run_bot():
    send_telegram("🤖 Bot started")

    while True:
        for symbol in SYMBOLS:
            try:
                print(f"Checking {symbol}...")

                closes = get_klines(symbol)
                signal = get_signal(symbol, closes)

                print(f"{symbol} signal:", signal)

                if signal:
                    msg = f"📊 {symbol} SIGNAL: {signal}"
                    send_telegram(msg)

            except Exception as e:
                print(f"Error on {symbol}:", e)

        print("Cycle complete. Sleeping...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
