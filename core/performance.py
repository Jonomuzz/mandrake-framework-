from core.accounting import load_trades
from collections import defaultdict

def compute_strategy_scores():

    trades = load_trades()

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

    scores = {}

    for s, v in stats.items():

        if v["trades"] == 0:
            continue

        win_rate = v["wins"] / v["trades"]
        avg_pnl = v["pnl"] / v["trades"]

        # simple composite score
        score = (win_rate * 0.6) + (avg_pnl * 0.4)

        scores[s] = score

    return scores
