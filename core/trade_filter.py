import time

# =========================
# COOLDOWN TRACKING
# =========================
last_trade_time = {}

# =========================
# CONFIG
# =========================
MIN_ZSCORE = 1.2
MIN_VOLUME_RATIO = 1.1
MIN_TREND_STRENGTH = 0.0005

COOLDOWN_SECONDS = 900  # 15 minutes


# =========================
# QUALITY FILTER
# =========================
def is_high_quality_setup(df, strategy, symbol):

    now = time.time()

    # =========================
    # COOLDOWN FILTER
    # =========================
    if symbol in last_trade_time:

        elapsed = now - last_trade_time[symbol]

        if elapsed < COOLDOWN_SECONDS:
            return False

    curr = df.iloc[-1]

    zscore = abs(curr.get("zscore", 0))
    volume = curr.get("volume", 0)
    volume_ma = curr.get("volume_ma", 1)

    trend_strength = abs(curr.get("trend_strength", 0))

    volume_ratio = (
        volume / volume_ma
        if volume_ma != 0 else 0
    )

    # =========================
    # MEAN REVERSION FILTER
    # =========================
    if strategy == "mean_reversion":

        if zscore < MIN_ZSCORE:
            return False

    # =========================
    # BREAKOUT FILTER
    # =========================
    elif strategy == "breakout":

        if volume_ratio < MIN_VOLUME_RATIO:
            return False

    # =========================
    # TREND FILTER
    # =========================
    elif strategy == "trend":

        if trend_strength < MIN_TREND_STRENGTH:
            return False

    return True


# =========================
# REGISTER TRADE
# =========================
def register_trade(symbol):

    last_trade_time[symbol] = time.time()
