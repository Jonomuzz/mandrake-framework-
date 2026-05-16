def init_strategy(strategy):
    if strategy not in strategy_stats:
        strategy_stats[strategy] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "disabled": False
        }
