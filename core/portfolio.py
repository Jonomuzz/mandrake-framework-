START_BALANCE = 500

portfolio = {
    "TOTAL": START_BALANCE,
    "SYMBOLS": {}
}


def init_symbol(symbol):
    if symbol not in portfolio["SYMBOLS"]:
        portfolio["SYMBOLS"][symbol] = {
            "balance": START_BALANCE,
            "positions": 0
        }


def update_balance(symbol, pnl):
    portfolio["SYMBOLS"][symbol]["balance"] += pnl
    portfolio["TOTAL"] += pnl


def get_balance(symbol):
    return portfolio["SYMBOLS"][symbol]["balance"]


def get_total_balance():
    return portfolio["TOTAL"]
