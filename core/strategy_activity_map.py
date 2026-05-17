from collections import defaultdict

activity = defaultdict(lambda: {
    "trend": 0,
    "mean_reversion": 0,
    "breakout": 0,
    "momentum": 0,
    "kst": 0,
    "signals": 0,
    "wins": 0,
    "losses": 0,
    "pnl": 0.0
})


def log_strategy(symbol, strategy):
    activity[symbol][strategy] += 1


def log_signal(symbol):
    activity[symbol]["signals"] += 1


def log_trade_result(symbol, pnl):
    if pnl > 0:
        activity[symbol]["wins"] += 1
    else:
        activity[symbol]["losses"] += 1

    activity[symbol]["pnl"] += pnl


def get_activity_report():
    report = "📊 REAL-TIME STRATEGY ACTIVITY MAP\n"

    for symbol, data in activity.items():

        total = (
            data["trend"] +
            data["mean_reversion"] +
            data["breakout"] +
            data["momentum"] +
            data["kst"]
        )

        if total == 0:
            continue

        report += f"\n{symbol}\n"

        for strat in ["trend", "mean_reversion", "breakout", "momentum", "kst"]:
            pct = (data[strat] / total) * 100
            report += f"- {strat}: {pct:.1f}%\n"

        report += f"- signals: {data['signals']}\n"
        report += f"- wins: {data['wins']} | losses: {data['losses']}\n"
        report += f"- pnl: {round(data['pnl'], 2)}\n"

    return report
