# core/analytics/strategy_activity_map.py

from collections import defaultdict

activity = defaultdict(lambda: {
    "trend": 0,
    "mean_reversion": 0,
    "breakout": 0,
    "momentum": 0,
    "kst": 0,
    "signals": 0
})


def log_strategy_usage(symbol, strategy):
    activity[symbol][strategy] += 1


def log_signal(symbol):
    activity[symbol]["signals"] += 1


def get_activity_report():
    report = "\n📊 STRATEGY ACTIVITY MAP\n"

    for symbol, data in activity.items():

        total = sum([
            data["trend"],
            data["mean_reversion"],
            data["breakout"],
            data["momentum"],
            data["kst"]
        ])

        if total == 0:
            continue

        report += f"\n{symbol}\n"

        for strat in ["trend", "mean_reversion", "breakout", "momentum", "kst"]:
            pct = (data[strat] / total) * 100 if total > 0 else 0
            report += f"- {strat}: {pct:.1f}%\n"

        report += f"- signals: {data['signals']}\n"

    return report
