from core.performance import compute_strategy_scores

capital_allocation = {
    "trend": 0.25,
    "mean_reversion": 0.25,
    "breakout": 0.25,
    "momentum": 0.25
}


def rebalance_capital():

    scores = compute_strategy_scores()

    total = sum(scores.values()) or 1

    for s in capital_allocation:

        if s in scores:
            capital_allocation[s] = max(0.05, scores[s] / total)

    return capital_allocation


def get_allocation(strategy):
    return capital_allocation.get(strategy, 0.1)
