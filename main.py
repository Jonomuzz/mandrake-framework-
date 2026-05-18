import time
import requests

from core.data import get_klines

from strategies.trend import get_signal as trend_signal
from strategies.mean_reversion import get_signal as mr_signal
from strategies.breakout import get_signal as breakout_signal
from strategies.momentum import get_signal as momentum_signal

from core.lifecycle_engine_v5 import (
    open_trade,
    manage_position,
    tick_cooldowns,
    positions
)

from core.portfolio_v5 import update_balance, summary

from core.control_panel import is_paused
from core.telegram_router import handle_command


# =========================
# CONFIG
# =========================

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

BALANCE = 500
RISK_PER_TRADE = 0.02

TELEGRAM_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

LAST_UPDATE_ID = 0


# =========================
# TELEGRAM SEND
# =========================

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("Telegram error:", e)


# =========================
# STRATEGIES
# =========================

def strategies():
    return {
        "trend": trend_signal,
        "mean_reversion": mr_signal,
        "breakout": breakout_signal,
        "momentum": momentum_signal
    }


# =========================
# COMMAND POLLING
# =========================

def check_telegram_commands():
    global LAST_UPDATE_ID

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

    try:
        res = requests.get(url).json()

        for update in res.get("result", []):

            update_id = update["update_id"]
            if update_id <= LAST_UPDATE_ID:
                continue

            LAST_UPDATE_ID = update_id

            if "message" in update:
                text = update["message"].get("text", "")

                response = handle_command(text)

                if response:
                    send_telegram(response)

    except Exception as e:
        print("Telegram command error:", e)


# =========================
# SYMBOL PROCESSING
# =========================

def process_symbol(symbol, df):

    price = df.iloc[-1]["close"]

    # 1. Manage existing position first
    trade = manage_position(symbol, price)

    if trade:
        update_balance(trade["pnl"])

    # 2. block new trades if paused
    if is_paused():
        return

    # 3. avoid duplicate positions
    if symbol in positions and positions[symbol]["open"]:
        return

    # 4. strategy evaluation
    for name, strat in strategies().items():

        signal = strat(df)

        if not signal:
            continue

        sl = price * (0.998 if signal == "BUY" else 1.002)
        tp = price * (0.003 + 1 if signal == "BUY" else 0.997)

        size = BALANCE * RISK_PER_TRADE

        open_trade(
            symbol=symbol,
            side=signal,
            price=price,
            sl=sl,
            tp=tp,
            size=size,
            strategy=name
        )

        send_telegram(f"{symbol} | {name.upper()} | {signal}")

        break


# =========================
# MAIN LOOP
# =========================

def run():

    print("🚀 V5 FULL POSITION + COMMAND ENGINE STARTED")
    send_telegram("🚀 FULL POSITION EXECUTION ENGINE STARTED")

    while True:

        # COMMAND HANDLER FIRST (important)
        check_telegram_commands()

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, "1m", 100)
                process_symbol(symbol, df)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        tick_cooldowns()

        summary()

        print("Cycle complete...\n")

        time.sleep(60)


if __name__ == "__main__":
    run()
