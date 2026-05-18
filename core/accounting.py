stats = {}

START_BALANCE = 500.0



def initialize_symbol(symbol):
    if symbol not in stats:
        stats[symbol] = {
            "balance": START_BALANCE,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0.0
        }



def record_trade(symbol, pnl):
    initialize_symbol(symbol)

    s = stats[symbol]

    s["trades"] += 1
    s["profit"] += pnl
    s["balance"] += pnl

    if pnl > 0:
        s["wins"] += 1
    else:
        s["losses"] += 1



def get_balance(symbol):
    initialize_symbol(symbol)
    return stats[symbol]["balance"]



def get_risk_amount(symbol, risk_pct=10):
    balance = get_balance(symbol)
    return balance * (risk_pct / 100)



def build_summary():

    total_balance = 0
    total_profit = 0
    total_trades = 0

    lines = []

    for symbol, s in stats.items():

        trades = s["trades"]
        wins = s["wins"]

        if trades > 0:
    return "\n".join(lines)
