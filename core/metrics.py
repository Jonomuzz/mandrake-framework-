strategy_stats = {}


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


def evaluate_strategies():
    """
    AUTO DISABLER (CRITICAL EDGE FEATURE)
    """

    for name, s in strategy_stats.items():

        if s["trades"] < 10:
            continue

        win_rate = s["wins"] / s["trades"]

        if win_rate < 0.40 and s["pnl"] < 0:
            s["disabled"] = True

        if win_rate > 0.55 and s["pnl"] > 0:
            s["disabled"] = False


def get_leaderboard():
    msg = "📊 STRATEGY LEADERBOARD\n\n"

    ranked = sorted(strategy_stats.items(), key=lambda x: x[1]["pnl"], reverse=True)

    for name, s in ranked:
        wr = (s["wins"] / s["trades"] * 100) if s["trades"] else 0

        status = "DISABLED" if s["disabled"] else "ACTIVE"

        msg += (
            f"{name} [{status}]\n"
            f"Trades: {s['trades']}\n"
            f"Win Rate: {wr:.1f}%\n"
            f"PnL: {s['pnl']:.2f}\n\n"
        )

    return msg
