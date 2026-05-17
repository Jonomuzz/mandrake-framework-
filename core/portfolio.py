import json
import os

PORTFOLIO_FILE = "storage/portfolio.json"

START_BALANCE = 500


# =========================
# INIT PORTFOLIO
# =========================
def init_portfolio(symbols):

    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)

    portfolio = {
        "TOTAL": {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0,
            "balance": START_BALANCE * len(symbols)
        }
    }

    for s in symbols:
        portfolio[s] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "profit": 0,
            "balance": START_BALANCE
        }

    save_portfolio(portfolio)
    return portfolio


# =========================
# SAVE
# =========================
def save_portfolio(portfolio):

    os.makedirs("storage", exist_ok=True)

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)


# =========================
# UPDATE AFTER TRADE
# =========================
def update_portfolio(portfolio, symbol, pnl_pct):

    sym = portfolio[symbol]
    total = portfolio["TOTAL"]

    sym["trades"] += 1
    total["trades"] += 1

    sym["profit"] += pnl_pct
    total["profit"] += pnl_pct

    if pnl_pct > 0:
        sym["wins"] += 1
        total["wins"] += 1
    else:
        sym["losses"] += 1
        total["losses"] += 1

    # compound balance
    sym["balance"] *= (1 + pnl_pct / 100)
    total["balance"] = sum(
        portfolio[s]["balance"]
        for s in portfolio
        if s != "TOTAL"
    )

    save_portfolio(portfolio)


# =========================
# FORMAT SUMMARY
# =========================
def format_summary(portfolio, symbol):

    sym = portfolio[symbol]
    total = portfolio["TOTAL"]

    win_rate = 0
    if sym["trades"] > 0:
        win_rate = (sym["wins"] / sym["trades"]) * 100

    total_win_rate = 0
    if total["trades"] > 0:
        total_win_rate = (total["wins"] / total["trades"]) * 100

    return f"""
📊 PERFORMANCE SUMMARY

{symbol}
Trades: {sym['trades']}
Win Rate: {round(win_rate, 2)}%
Profit: {round(sym['profit'], 2)}%
Balance: ${round(sym['balance'], 2)}

TOTAL
Trades: {total['trades']}
Win Rate: {round(total_win_rate, 2)}%
Profit: {round(total['profit'], 2)}%
Balance: ${round(total['balance'], 2)}
"""
