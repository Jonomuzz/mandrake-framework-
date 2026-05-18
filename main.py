import os
import time
import pandas as pd
import requests

from core.positions import open_position, get_all_positions
from strategies.trend import get_signal as trend_signal
from strategies.breakout import get_signal as breakout_signal
from strategies.momentum import get_signal as momentum_signal
from strategies.mean_reversion import get_signal as mean_reversion_signal

# =========================
# CONFIG
# =========================

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

# =========================
# TELEGRAM
# =========================

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("Telegram error:", e)

# =========================
# DATA
# =========================

def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    data = requests.get(BASE_URL, params=params).json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["open"] = df["open"].astype(float)

    return df

# =========================
# STRATEGY ROUTER
# =========================

def get_signal(df, symbol):
    """
    Simple router (you already evolved this earlier)
    """
    if symbol in ["BTCUSDT", "ETHUSDT"]:
        return trend_signal(df)

    if symbol in ["XRPUSDT", "ADAUSDT", "DOGEUSDT"]:
        return breakout_signal(df)

    if symbol in ["SOLUSDT", "AVAXUSDT", "LINKUSDT"]:
        return momentum_signal(df)

    return mean_reversion_signal(df)

# =========================
# POSITION MANAGEMENT (V6)
# =========================

def evaluate_positions(price_map):
    """
    SL/TP lifecycle engine
    """

    positions = get_all_positions()

    for pos in positions:

        if pos["status"] != "OPEN":
            continue

        symbol = pos["symbol"]
        price = price_map.get(symbol)

        if price is None:
            continue

        # BUY logic
        if pos["side"] == "BUY":

            if price <= pos["sl"]:
                pos["status"] = "CLOSED"
                pos["exit_price"] = price
                pnl = (price - pos["entry"]) * pos["qty"]
                pos["pnl"] = pnl

                send_telegram(f"🔴 STOP LOSS HIT {symbol} | PnL: {pnl:.2f}")

            elif price >= pos["tp"]:
                pos["status"] = "CLOSED"
                pos["exit_price"] = price
                pnl = (price - pos["entry"]) * pos["qty"]
                pos["pnl"] = pnl

                send_telegram(f"🟢 TAKE PROFIT HIT {symbol} | PnL: {pnl:.2f}")

        # SELL logic
        else:

            if price >= pos["sl"]:
                pos["status"] = "CLOSED"
                pos["exit_price"] = price
                pnl = (pos["entry"] - price) * pos["qty"]
                pos["pnl"] = pnl

                send_telegram(f"🔴 STOP LOSS HIT {symbol} | PnL: {pnl:.2f}")

            elif price <= pos["tp"]:
                pos["status"] = "CLOSED"
                pos["exit_price"] = price
                pnl = (pos["entry"] - price) * pos["qty"]
                pos["pnl"] = pnl

                send_telegram(f"🟢 TAKE PROFIT HIT {symbol} | PnL: {pnl:.2f}")

# =========================
# MAIN LOOP
# =========================

def run():
    send_telegram("🚀 V6 FULL POSITION LIFECYCLE ENGINE STARTED")

    print("🚀 V6 ENGINE STARTED")

    while True:

        price_map = {}

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol)
                price = df["close"].iloc[-1]

                price_map[symbol] = price

                signal = get_signal(df, symbol)

                if signal:

                    # simple risk model (can upgrade later)
                    qty = 10

                    sl = price * (0.99 if signal == "BUY" else 1.01)
                    tp = price * (1.02 if signal == "BUY" else 0.98)

                    open_position(
                        symbol=symbol,
                        side=signal,
                        entry_price=price,
                        qty=qty,
                        sl=sl,
                        tp=tp,
                        strategy="V6_ROUTER"
                    )

                    send_telegram(
                        f"🟢 OPEN {signal} {symbol} @ {price:.4f} | SL {sl:.4f} TP {tp:.4f}"
                    )

                print(f"{symbol} | {signal}")

            except Exception as e:
                print(f"Error {symbol}:", e)

        # 🔥 THIS IS THE CORE V6 LIFECYCLE STEP
        evaluate_positions(price_map)

        print("Cycle complete...\n")
        time.sleep(SLEEP)

# =========================
# START
# =========================

if __name__ == "__main__":
    run()
