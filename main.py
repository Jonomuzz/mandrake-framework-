import os
import traceback
import time

from core.data import get_klines
from core.notifications import send_telegram

# Import strategies safely
from strategies.mean_reversion import get_signal as mean_reversion_signal
from strategies.trend import get_signal as trend_signal
from strategies.momentum import get_signal as momentum_signal
from strategies.breakout import get_signal as breakout_signal


SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100


def select_strategy(symbol, df):
    """
    Simple router (you can improve later)
    """
    if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        return "trend"
    elif symbol in ["SOLUSDT", "AVAXUSDT", "LINKUSDT"]:
        return "momentum"
    elif symbol in ["XRPUSDT", "ADAUSDT", "DOGEUSDT"]:
        return "breakout"
    else:
        return "mean_reversion"


def run_strategy(strategy_name, df, symbol):
    """
    Central execution wrapper (IMPORTANT FOR DEBUGGING)
    """
    print(f"▶ Running strategy: {strategy_name} | {symbol}")

    if strategy_name == "trend":
        return trend_signal(df)

    if strategy_name == "momentum":
        return momentum_signal(df)

    if strategy_name == "breakout":
        return breakout_signal(df)

    return mean_reversion_signal(df)


def run():
    print("🚀 FULL EXECUTION ENGINE STARTED")
    send_telegram("🚀 FULL EXECUTION ENGINE STARTED")

    while True:

        for symbol in SYMBOLS:
            try:
                print(f"\n📊 Processing {symbol}")

                # STEP 1: Get data
                df = get_klines(symbol, INTERVAL, LIMIT)

                # STEP 2: Choose strategy
                strategy = select_strategy(symbol, df)

                # STEP 3: Run strategy
                signal = run_strategy(strategy, df, symbol)

                # STEP 4: Output
                print(f"{symbol} | {strategy} | {signal}")

                # STEP 5: Notify only real signals
                if signal:
                    msg = f"{symbol} | {strategy.upper()} | {signal}"
                    send_telegram(msg)

            except Exception as e:
                print(f"\n❌ ERROR IN SYMBOL: {symbol}")
                print(traceback.format_exc())  # 🔥 THIS IS THE KEY CHANGE

        print("Cycle complete...\n")
        time.sleep(5)


if __name__ == "__main__":
    run()
