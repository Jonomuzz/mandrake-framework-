import numpy as np

state = {
    "equity": 500,
    "peak_equity": 500,
    "drawdown": 0
}

STRATEGY_STATS = {
    "trend": {"wins": 0, "losses": 0},
    "breakout": {"wins": 0, "losses": 0},
    "mean_reversion": {"wins": 0, "losses": 0},
    "momentum": {"wins": 0, "losses": 0},
}


# =========================
# EQUITY UPDATE
# =========================

def update_equity(pnl):
    state["equity"] += pnl

    if state["equity"] > state["peak_equity"]:
        state["peak_equity"] = state["equity"]

    state["drawdown"] = (state["peak_equity"] - state["equity"]) / state["peak_equity"]


def risk_kill_switch():
    return state["drawdown"] > 0.15  # 15% max drawdown


# =========================
# STRATEGY SCORING
# =========================

def strategy_weight(name):
    stats = STRATEGY_STATS.get(name, {"wins": 1, "losses": 1})

    total = stats["wins"] + stats["losses"]

    if total == 0:
        return 1.0

    winrate = stats["wins"] / total

    if winrate < 0.4:
        return 0.3
    elif winrate < 0.5:
        return 0.6
    elif winrate < 0.6:
        return 1.0
    else:
        return 1.4


def update_strategy(name, win):
    if name not in STRATEGY_STATS:
        STRATEGY_STATS[name] = {"wins": 0, "losses": 0}

    if win:
        STRATEGY_STATS[name]["wins"] += 1
    else:
        STRATEGY_STATS[name]["losses"] += 1
