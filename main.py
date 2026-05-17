import os
import time
import pandas as pd

from core.data import get_klines
from core.notifications import send_telegram
from core.execution import process_trade
from core.portfolio import init_portfolio, format_summary

# strategies
from strategies.mean_reversion import get_signal as mean_reversion_signal
from strategies.trend_strength_crossover import get_signal as trend_signal
from strategies.momentum import get_signal as momentum_signal
from strategies.breakout import get_signal as breakout_signal


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


# =========================
# PORTFOLIO INIT
# =========================

portfolio = init_portfolio(SYMBOLS)


# =========================
# STRATEGY ROUTER
# =========================

def get_strategy_signal(df, symbol):

    # simple regime logic (stable version)
    if df["close"].iloc[-1] > df["close"].rolling(20).mean().iloc[-1]:
        return trend_signal(df)
    elif df["close"].pct_change().std() > 0.01:
        return momentum_signal(df)
    elif df["close"].pct_change().abs().mean() < 0.002:
        return mean_reversion_signal(df)
    else:
        return breakout_signal(df)


# =========================
# RUN LOOP
# =========================

def run():

    send_telegram("🚀 FULL EXECUTION ENGINE STARTED")

    while True:

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, INTERVAL, LIMIT)

                if df is None or len(df) < 30:
                    continue

                price = float(df["close"].iloc[-1])

                signal = get_strategy_signal(df, symbol)

                print(f"{symbol} | {signal}")

                # EXECUTION
                process_trade(symbol, signal, price, portfolio)

                # OPTIONAL: periodic summary
                if signal in ["BUY", "SELL"]:
                    send_telegram(format_summary(portfolio, symbol))

            except Exception as e:
                print(f"Error {symbol}: {e}")

        print("Cycle complete...")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
