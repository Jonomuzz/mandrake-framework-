from core.accounting import load_trades
from collections import defaultdict


def generate_dashboard():

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

    report = "📊 STRATEGY PERFORMANCE DASHBOARD\n"

    ranked = []

    for s, v in stats.items():

        if v["trades"] == 0:
            continue

        win_rate = v["wins"] / v["trades"]
        avg_pnl = v["pnl"] / v["trades"]
        efficiency = win_rate * avg_pnl

        ranked.append((efficiency, s, v))

    ranked.sort(reverse=True)

    for score, s, v in ranked:

        report += f"\n{s.upper()}\n"
        report += f"- Trades: {v['trades']}\n"
        report += f"- Win Rate: {round(v['wins']/v['trades']*100, 2)}%\n"
        report += f"- PnL: {round(v['pnl'], 2)}\n"
        report += f"- Score: {round(score, 4)}\n"

    return report
