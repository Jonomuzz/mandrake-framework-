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

from core.analytics.strategy_activity_map import (
    log_strategy,
    log_signal,
    log_trade_result,
    get_activity_report
)

# ================= CONFIG =================
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100
SLEEP = 60

START_BALANCE = 500
RISK_PER_TRADE = 0.10

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

BASE_URL = "https://api.binance.com/api/v3/klines"

# ================= STATE =================
positions = {}        # symbol -> open/closed
entry_price = {}      # symbol -> price
position_size = {}    # symbol -> usd size


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


# ================= ROUTER =================
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

    # ================= ENTRY =================
    if signal == "BUY" and positions.get(symbol) is None:

        positions[symbol] = "LONG"
        entry_price[symbol] = price
        position_size[symbol] = START_BALANCE * RISK_PER_TRADE

        log_signal(symbol)

        msg = f"🟢 BUY {symbol} | {strategy} @ {price}"
        send_telegram(msg)

    # ================= EXIT =================
    if signal == "SELL" and positions.get(symbol) == "LONG":

        entry = entry_price[symbol]
        size = position_size[symbol]

        pnl_pct = ((price - entry) / entry) * 100
        pnl_usd = size * (pnl_pct / 100)

        log_trade_result(symbol, pnl_usd)

        msg = (
            f"🔴 SELL {symbol} | {strategy} @ {price}\n"
            f"PnL: {round(pnl_pct, 2)}% | ${round(pnl_usd, 2)}"
        )

        send_telegram(msg)

        positions[symbol] = None
        entry_price[symbol] = 0
        position_size[symbol] = 0


# ================= MAIN LOOP =================
def run():

    print("🚀 FULL REAL TRADING BRAIN STARTED")
    send_telegram("🚀 FULL REAL TRADING BRAIN STARTED")

    last_report = time.time()

    while True:

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol)

                strategy = select_strategy(df)
                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                log_strategy(symbol, strategy)

                print(f"{symbol} | {strategy} | {signal}")

                if signal:
                    execute_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        # ================= REPORT =================
        if time.time() - last_report > 900:
            send_telegram(get_activity_report())
            last_report = time.time()

        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
