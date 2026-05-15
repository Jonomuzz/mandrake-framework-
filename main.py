print("MAIN.PY STARTING")

import time

print("IMPORTING CONFIG")

from core.config import ACTIVE_STRATEGY
from core.config import PAIRS
from core.config import SLEEP
from core.config import START_BALANCE_PER_PAIR

print("IMPORTING DATA")

from core.data import get_klines

print("IMPORTING TELEGRAM")

from core.telegram import send_telegram

print("IMPORTING METRICS")

from core.metrics import (
    load_metrics,
    update_metrics,
    calculate_advanced_metrics
)

print("LOADING STRATEGY")

if ACTIVE_STRATEGY == "trend":
    from strategies.trend import calculate_indicators
    from strategies.trend import check_signal

elif ACTIVE_STRATEGY == "mean_reversion":
    from strategies.mean_reversion import calculate_indicators
    from strategies.mean_reversion import check_signal

elif ACTIVE_STRATEGY == "breakout":
    from strategies.breakout import calculate_indicators
    from strategies.breakout import check_signal

elif ACTIVE_STRATEGY == "momentum":
    from strategies.momentum import calculate_indicators
    from strategies.momentum import check_signal

elif ACTIVE_STRATEGY == "kst":
    from strategies.kst import calculate_indicators
    from strategies.kst import check_signal

else:
    raise Exception(f"Unknown strategy: {ACTIVE_STRATEGY}")

print("STRATEGY LOADED")

balances = {}
positions = {}

print("INITIALIZING PAIRS")

for pair in PAIRS:

    balances[pair] = START_BALANCE_PER_PAIR
    positions[pair] = None

print("LOADING METRICS FILE")

metrics = load_metrics()

print("FRAMEWORK BOT RUNNING")

send_telegram(
    f"Bot Started - Strategy: {ACTIVE_STRATEGY}"
)

while True:

    for pair in PAIRS:

        try:

            print(f"Checking {pair}...")

            df = get_klines(pair)

            df = calculate_indicators(df)

            signal = check_signal(df)

            print(f"{pair} signal: {signal}")

            # =========================
            # SIGNAL ALERTS
            # =========================
            if signal is not None:

                send_telegram(
                    f"📈 SIGNAL DETECTED\n\n"
                    f"Strategy: {ACTIVE_STRATEGY}\n"
                    f"Pair: {pair}\n"
                    f"Signal: {signal}"
                )

        except Exception as e:

            print(f"ERROR WITH {pair}: {e}")

    print("Cycle complete. Sleeping...")

    time.sleep(SLEEP)

    for pair in PAIRS:

        try:

            print(f"Checking {pair}...")

            df = get_klines(pair)

            df = calculate_indicators(df)

            signal = check_signal(df)

            print(f"{pair} signal: {signal}")

        except Exception as e:

            print(f"ERROR WITH {pair}: {e}")

    print("Cycle complete. Sleeping...")

    time.sleep(SLEEP)
