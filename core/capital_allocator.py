from core.accounting import load_trades
from collections import defaultdict

# =========================
# CONFIG
# =========================

MIN_ALLOCATION = 0.05   # 5%
MAX_ALLOCATION = 0.40   # 40%
DEFAULT_ALLOCATION = 0.10

LOOKBACK_TRADES = 200

allocations = {
    "trend": 0.25,
    "mean_reversion": 0.25,
    "breakout": 0.25,
    "momentum": 0.25,
    "kst": 0.25
}


# =========================
# COMPUTE STRATEGY STATS
# =========================

def compute_stats():

    trades = load_trades()[-LOOKBACK_TRADES:]

    stats = defaultdict(lambda: {
        "wins": 0,
        "losses": 0,
        "pnl": 0.0,
        "trades": 0
    })

    for t in trades:
        s = t["strategy"]
        pnl = t["pnl"]

        stats[s]["trades"] += 1
        stats[s]["pnl"] += pnl

        if pnl > 0:
            stats[s]["wins"] += 1
        else:
            stats[s]["losses"] += 1

    return stats


# =========================
# ALLOCATION ENGINE v2
# =========================

def rebalance_capital():

    stats = compute_stats()

    scores = {}

    total_score = 0

    for s, v in stats.items():

        if v["trades"] < 5:
            scores[s] = 0.5
            continue

        win_rate = v["wins"] / v["trades"]
        avg_pnl = v["pnl"] / v["trades"]

        # core performance score
        score = (win_rate * 0.7) + (avg_pnl * 0.3)

        # penalise drawdown-heavy strategies
        if v["pnl"] < 0:
            score *= 0.7

        scores[s] = max(0.1, score)
        total_score += scores[s]

    if total_score == 0:
        return allocations

    # normalize allocations
    new_allocations = {}

    for s, score in scores.items():

        weight = score / total_score

        # clamp exposure
        weight = max(MIN_ALLOCATION, min(MAX_ALLOCATION, weight))

        new_allocations[s] = weight

    # ensure sum stability (simple normalisation fix)
    total = sum(new_allocations.values())

    for s in new_allocations:
        new_allocations[s] = round(new_allocations[s] / total, 3)

    allocations.update(new_allocations)

    return allocations


# =========================
# GET ALLOCATION
# =========================

def get_allocation(strategy):
    return allocations.get(strategy, DEFAULT_ALLOCATION)


# =========================
# DEBUG REPORT
# =========================

def get_allocation_report():

    report = "💰 CAPITAL ALLOCATION v2\n\n"

    for s, w in allocations.items():
        report += f"{s}: {round(w * 100, 2)}%\n"

    return report
