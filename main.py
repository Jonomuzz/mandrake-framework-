import time

from core.config import ACTIVE_STRATEGY
from core.config import PAIRS
from core.config import SLEEP
from core.config import START_BALANCE_PER_PAIR

from core.data import get_klines
from core.telegram import send_telegram

from core.metrics import (
    load_metrics,
    update_metrics,
    calculate_advanced_metrics
)


# =========================
# STRATEGY LOADER
# =========================
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


# =========================
# PAPER TRADING STATE
# =========================
balances = {}
positions = {}


# =========================
# INITIALIZE
# =========================
for pair in PAIRS:

    balances[pair] = START_BALANCE_PER_PAIR
    positions[pair] = None
    time.sleep(SLEEP)
