trade_stats = {
    "total_trades": 0,
    "wins": 0,
    "losses": 0,
    "profit": 0
}


def record_trade(pnl_pct):

    trade_stats["total_trades"] += 1

    trade_stats["profit"] += pnl_pct

    if pnl_pct > 0:
        trade_stats["wins"] += 1
    else:
        trade_stats["losses"] += 1


def get_summary():

    total = trade_stats["total_trades"]

    win_rate = 0

    if total > 0:
        win_rate = (
            trade_stats["wins"] / total
        ) * 100

    return {
        "trades": total,
        "win_rate": round(win_rate, 2),
        "profit": round(trade_stats["profit"], 2)
    }
