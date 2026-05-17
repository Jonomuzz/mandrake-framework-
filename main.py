import os
import time

from core.data import get_klines
from core.notifications import send_telegram

from strategies.mean_reversion import get_signal as mean_reversion
from strategies.trend_strength_crossover import get_signal as trend
from strategies.momentum import get_signal as momentum
from strategies.breakout import get_signal as breakout
from strategies.kst import get_signal as kst


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

STRATEGY_MAP = {
    "mean_reversion": mean_reversion,
    "trend": trend,
    "momentum": momentum,
    "breakout": breakout,
    "kst": kst
}

# simple overtrade protection (cooldown per symbol)
cooldown = {}
COOLDOWN_CYCLES = 3


# =========================
# STRATEGY SELECTOR
# =========================

def select_strategy(symbol):
    """
    Simple deterministic routing (can be upgraded later)
    """
    if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        return "trend"
    elif symbol in ["SOLUSDT", "AVAXUSDT", "LTCUSDT"]:
        return "momentum"
    elif symbol in ["DOGEUSDT", "XRPUSDT"]:
        return "breakout"
    else:
        return "mean_reversion"


# =========================
# COOLDOWN FILTER
# =========================

def can_trade(symbol):
    return cooldown.get(symbol, 0) == 0


def apply_cooldown(symbol):
    cooldown[symbol] = COOLDOWN_CYCLES


def reduce_cooldowns():
    for k in list(cooldown.keys()):
        cooldown[k] -= 1
        if cooldown[k] <= 0:
            del cooldown[k]


# =========================
# MAIN LOOP
# =========================

def run():
    print("🚀 FULL EXECUTION ENGINE STARTED")

    send_telegram("🚀 FULL EXECUTION ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, INTERVAL, LIMIT)

                strategy_name = select_strategy(symbol)
                strategy = STRATEGY_MAP[strategy_name]

                signal = strategy(df)

                print(f"{symbol} | {strategy_name} | {signal}")

                # only act on real signals
                if signal and can_trade(symbol):

                    msg = f"{symbol} | {strategy_name.upper()} | {signal}"
                    send_telegram(msg)

                    apply_cooldown(symbol)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        reduce_cooldowns()
        print("Cycle complete...\n")
        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
