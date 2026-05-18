import time
import traceback

from core.data import get_klines
from core.notifications import send_telegram
from core.execution import process_trade, check_positions
from core.accounting import build_summary

from strategies.trend import get_signal as trend_signal
from strategies.mean_reversion import get_signal as mean_reversion_signal
from strategies.momentum import get_signal as momentum_signal
from strategies.breakout import get_signal as breakout_signal


# =========================
# CONFIG
# =========================

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "LTCUSDT",
    "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100
SLEEP_SECONDS = 30

# prevents duplicate spam signals
last_signals = {}


# =========================
# STRATEGY ROUTER
# =========================

def select_strategy(symbol):
    if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        return "trend"

    if symbol in ["SOLUSDT", "AVAXUSDT", "LINKUSDT"]:
        return "momentum"

    if symbol in ["XRPUSDT", "ADAUSDT", "DOGEUSDT"]:
        return "breakout"

    return "mean_reversion"


def get_signal(strategy, df):
    if strategy == "trend":
        return trend_signal(df)

    if strategy == "momentum":
        return momentum_signal(df)

    if strategy == "breakout":
        return breakout_signal(df)

    return mean_reversion_signal(df)


# =========================
# MAIN ENGINE
# =========================

def run():

    print("🚀 FULL POSITION EXECUTION ENGINE STARTED")
    send_telegram("🚀 FULL POSITION EXECUTION ENGINE STARTED")

    cycle = 0

    while True:

        for symbol in SYMBOLS:

            try:

                # =========================
                # DATA
                # =========================
                df = get_klines(symbol, INTERVAL, LIMIT)
                current_price = float(df.iloc[-1]["close"])

                # =========================
                # STRATEGY
                # =========================
                strategy = select_strategy(symbol)
                signal = get_signal(strategy, df)

                print(f"{symbol} | {strategy} | {signal}")

                # =========================
                # POSITION MANAGEMENT
                # =========================
                check_positions(symbol, current_price)

                # =========================
                # DUPLICATE FILTER
                # =========================
                if signal == last_signals.get(symbol):
                    continue

                last_signals[symbol] = signal

                # =========================
                # EXECUTION
                # =========================
                if signal:
                    process_trade(symbol, signal, current_price)

            except Exception:
                print(f"\n❌ ERROR IN {symbol}")
                print(traceback.format_exc())

        cycle += 1

        # =========================
        # SUMMARY REPORT
        # =========================
        if cycle % 20 == 0:
            summary = build_summary()
            print(summary)
            send_telegram(summary)

        print("Cycle complete...\n")
        time.sleep(SLEEP_SECONDS)


# =========================
# ENTRY POINT (IMPORTANT)
# =========================

if __name__ == "__main__":
    run()
