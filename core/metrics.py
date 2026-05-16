strategy_stats = {}
capital_rotation_state = {}
correlation_exposure = {}

# =========================
# STRATEGY PERFORMANCE
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

    for name, s in strategy_stats.items():

        if s["trades"] == 0:
            continue

        win_rate = s["wins"] / s["trades"]

        # combined performance score
        scores[name] = s["pnl"] * win_rate


    if not scores:
        return

    best = max(scores.values())
    worst = min(scores.values())

    for name, score in scores.items():

        if name not in capital_rotation_state:
            capital_rotation_state[name] = {
                "allocation": 1.0,
                "disabled": False
            }

        if best == worst:
            norm = 1.0
        else:
            norm = (score - worst) / (best - worst)

        allocation = 0.3 + (norm * 1.7)

        capital_rotation_state[name]["allocation"] = allocation

        # AUTO DISABLE RULES
        if score < -0.5:
            capital_rotation_state[name]["disabled"] = True
        elif score > 0:
            capital_rotation_state[name]["disabled"] = False


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


def update_correlation(symbol):

    for group, symbols in CORRELATION_GROUPS.items():

        if symbol in symbols:

            correlation_exposure[group] = correlation_exposure.get(group, 0) + 1


def correlation_block(symbol):

    for group, symbols in CORRELATION_GROUPS.items():

        if symbol in symbols:

            exposure = correlation_exposure.get(group, 0)

            if exposure > 3:
                return True

    return False


def reset_correlation():
    global correlation_exposure
    correlation_exposure = {}
