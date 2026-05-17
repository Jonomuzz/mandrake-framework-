import time
import os
import requests
import pandas as pd
from collections import defaultdict

from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)

# ================= CORE SYSTEM =================
from core.accounting import log_trade
from core.strategy_guard import evaluate_strategies, is_disabled
from core.correlation import register_position, remove_position, is_correlated_block

from core.exits import should_exit
from core.dashboard import generate_dashboard
from core.capital_allocator import rebalance_capital, get_allocation, get_allocation_report

# ================= CONFIG =================
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100
SLEEP = 60

START_BALANCE = 500

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BASE_URL = "https://api.binance.com/api/v3/klines"

# ================= STATE =================
positions = {}
entry_price = {}
position_size = {}
entry_time = {}
last_report = time.time()

# ================= TELEGRAM =================
def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
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
    df["volume"] = df[5].astype(float)
    return df

# ================= REGIME =================
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

# ================= SIGNAL ROUTER =================
def get_signal(df, strategy):

    if strategy == "trend":
        df = trend_strength_crossover.calculate_indicators(df)
        return trend_strength_crossover.check_signal(df)

    if strategy == "mean_reversion":
        return mean_reversion.check_signal(df)

    if strategy == "breakout":
        return breakout.check_signal(df)

    if strategy == "momentum":
        return momentum.check_signal(df)

    if strategy == "kst":
        return kst.check_signal(df)

    return None

# ================= EXECUTION =================
def execute_trade(symbol, signal, price, strategy):

    global positions

    now = time.time()

    # ================= ENTRY =================
    if signal == "BUY" and positions.get(symbol) is None:

        allocation = get_allocation(strategy)
        size = START_BALANCE * allocation

        positions[symbol] = "LONG"
        entry_price[symbol] = price
        position_size[symbol] = size
        entry_time[symbol] = now

        register_position(symbol, strategy)

        msg = f"🟢 BUY {symbol} | {strategy} | size=${round(size,2)} @ {price}"
        send_telegram(msg)

    # ================= EXIT =================
    elif positions.get(symbol) == "LONG":

        exit_reason = should_exit(
            symbol,
            entry_price[symbol],
            price,
            entry_time[symbol],
            regime_flip=False
        )

        if signal == "SELL" or exit_reason is not None:

            entry = entry_price[symbol]
            size = position_size[symbol]

            pnl_pct = ((price - entry) / entry) * 100
            pnl_usd = size * (pnl_pct / 100)

            log_trade(symbol, strategy, "LONG", entry, price, size, pnl_usd)
            remove_position(symbol)

            positions[symbol] = None
            entry_price[symbol] = 0
            position_size[symbol] = 0

            msg = (
                f"🔴 SELL {symbol} | {strategy}\n"
                f"PnL: {round(pnl_pct,2)}% | ${round(pnl_usd,2)}\n"
                f"Exit: {exit_reason if exit_reason else 'signal'}"
            )

            send_telegram(msg)

# ================= MAIN LOOP =================
def run():

    print("🚀 FULL CAPITAL ALLOCATOR v2 ENGINE STARTED")
    send_telegram("🚀 FULL CAPITAL ALLOCATOR v2 ENGINE STARTED")

    while True:

        evaluate_strategies()
        rebalance_capital()

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)

                if is_disabled(strategy):
                    continue

                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                if signal:
                    execute_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        # ================= REPORTS =================
        global last_report

        if time.time() - last_report > 900:

            send_telegram(generate_dashboard())
            send_telegram(get_allocation_report())

            last_report = time.time()

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
