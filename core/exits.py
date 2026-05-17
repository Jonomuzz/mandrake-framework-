import time

trailing_stop = {}
peak_price = {}

TRAILING_PCT = 0.004  # 0.4%
MAX_HOLD_TIME = 60 * 30  # 30 minutes


def update_trailing(symbol, price):

    if symbol not in peak_price:
        peak_price[symbol] = price

    peak_price[symbol] = max(peak_price[symbol], price)


def should_exit(symbol, entry_price, current_price, start_time, regime_flip=False):

    update_trailing(symbol, current_price)

    # 1. TRAILING STOP
    trail_stop_price = peak_price[symbol] * (1 - TRAILING_PCT)

    if current_price < trail_stop_price:
        return "TRAIL_STOP"

    # 2. REGIME FLIP EXIT
    if regime_flip:
        return "REGIME_FLIP"

    # 3. TIME EXIT
    if time.time() - start_time > MAX_HOLD_TIME:
        return "TIME_EXIT"

    return None
