strategy_stats = {}
capital_rotation_state = {}
correlation_state = {}

# =========================
# STRATEGY TRACKING
# =========================
def update_strategy_metrics(strategy, pnl):
    if strategy not in strategy_stats:
        strategy_stats[strategy] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "disabled": False
        }

    s = strategy_stats[strategy]

    s["trades"] += 1
    s["pnl"] += pnl

    if pnl > 0:
        s["wins"] += 1
    else:
        s["losses"] += 1


# =========================
# CAPITAL ROTATION ENGINE
# =========================
def update_capital_rotation():

    if not strategy_stats:
        return

    scores = {}

    for k, v in strategy_stats.items():
        if v["trades"] == 0:
            continue

        win_rate = v["wins"] / v["trades"]
        scores[k] = v["pnl"] * win_rate


    if not scores:
        return

    best = max(scores.values())
    worst = min(scores.values())

    for k, score in scores.items():

        if k not in capital_rotation_state:
            capital_rotation_state[k] = {
                "allocation": 1.0,
                "disabled": False
            }

        if best == worst:
            norm = 1.0
        else:
            norm = (score - worst) / (best - worst)

        allocation = 0.3 + (norm * 1.7)

        capital_rotation_state[k]["allocation"] = allocation

        # auto disable
        if score < -0.5:
            capital_rotation_state[k]["disabled"] = True
        elif score > 0:
            capital_rotation_state[k]["disabled"] = False


def get_allocation(strategy):
    if strategy not in capital_rotation_state:
        return 1.0
    return capital_rotation_state[strategy]["allocation"]


def is_disabled(strategy):
    return capital_rotation_state.get(strategy, {}).get("disabled", False)


# =========================
# CORRELATION RISK ENGINE
# =========================
CORRELATION_GROUPS = {
    "BTC_GROUP": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"],
    "ALT_GROUP": ["XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT"],
    "SMALL_GROUP": ["LTCUSDT", "ATOMUSDT"]
}

correlation_exposure = {}


def update_correlation(symbol, signal_strength=1):

    for group, symbols in CORRELATION_GROUPS.items():

        if symbol in symbols:

            if group not in correlation_exposure:
                correlation_exposure[group] = 0

            correlation_exposure[group] += signal_strength


def correlation_block(symbol):

    for group, symbols in CORRELATION_GROUPS.items():

        if symbol in symbols:

            exposure = correlation_exposure.get(group, 0)

            # limit overexposure
            if exposure > 3:
                return True

    return False
