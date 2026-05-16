import time
import requests
import os
from collections import defaultdict
import pandas as pd

from strategies import mean_reversion, trend, breakout, momentum
from analytics import load, save, update_trade, compute_metrics

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
# ENV
# ----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BOT_NAME = os.getenv("BOT_NAME", "mandrake-bot")
ACTIVE_STRATEGY = os.getenv("ACTIVE_STRATEGY", "trend")

# ----------------------------
# ANALYTICS STATE
# ----------------------------
analytics = load()

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
# TRADE SIMULATION (ENTRY/EXIT ENGINE)
# ----------------------------
positions = {}  # key: (bot, symbol)


def open_position(bot, symbol, side, price):
    positions[(bot, symbol)] = {
        "side": side,
        "entry": price
    }


def close_position(bot, symbol, price):
    key = (bot, symbol)

    if key not in positions:
        return None

    pos = positions.pop(key)
    entry = pos["entry"]

    if pos["side"] == "BUY":
        pnl = ((price - entry) / entry) * 100
    else:
        pnl = ((entry - price) / entry) * 100

    return {
        "symbol": symbol,
        "side": pos["side"],
        "entry": entry,
        "exit": price,
        "pnl": pnl
    }

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
                price = df.iloc[-1]["close"]

                signal = get_signal(df)

                # ----------------------------
                # ENTRY
                # ----------------------------
                if signal == "BUY":
                    if (BOT_NAME, symbol) not in positions:
                        open_position(BOT_NAME, symbol, "BUY", price)

                        send_telegram(
                            f"🟢 {BOT_NAME} | {ACTIVE_STRATEGY}\n"
                            f"OPEN BUY {symbol} @ {price}"
                        )

                # ----------------------------
                # EXIT
                # ----------------------------
                elif signal == "SELL":
                    trade = close_position(BOT_NAME, symbol, price)

                    if trade:
                        update_trade(analytics, BOT_NAME, symbol, trade["pnl"])
                        save(analytics)

                        metrics = compute_metrics(analytics[BOT_NAME][symbol])

                        send_telegram(
                            f"🔴 {BOT_NAME} | {ACTIVE_STRATEGY}\n"
                            f"CLOSE TRADE {symbol}\n"
                            f"PnL: {trade['pnl']:.2f}%\n"
                            f"Entry: {trade['entry']}\n"
                            f"Exit: {trade['exit']}\n\n"
                            f"📊 METRICS\n"
                            f"Trades: {metrics['trades']}\n"
                            f"Win Rate: {metrics['win_rate']:.1f}%\n"
                            f"Profit: {metrics['profit']}\n"
                            f"Max DD: {metrics['max_drawdown']}"
                        )

            except Exception as e:
                print(f"Error {symbol}:", e)

        print("Cycle complete. Sleeping...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_bot()
