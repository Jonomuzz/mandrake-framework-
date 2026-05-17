from core.accounting import load_trades
from collections import defaultdict

disabled = set()


def evaluate_strategies():

    trades = load_trades()

    stats = defaultdict(lambda: {"wins": 0, "losses": 0})

    for t in trades[-200:]:
        s = t["strategy"]

        if t["pnl"] > 0:
            stats[s]["wins"] += 1
        else:
            stats[s]["losses"] += 1

    for s, v in stats.items():

        total = v["wins"] + v["losses"]

        if total < 10:
            continue

        winrate = v["wins"] / total

        if winrate < 0.4:
            disabled.add(s)

        if winrate > 0.55 and s in disabled:
            disabled.remove(s)


def is_disabled(strategy):
    return strategy in disabled
