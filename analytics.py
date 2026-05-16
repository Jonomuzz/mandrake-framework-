import os
import json
from datetime import datetime

FILE = "storage/analytics.json"


# ----------------------------
# LOAD / SAVE
# ----------------------------
def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)


def save(data):
    os.makedirs("storage", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# ----------------------------
# INIT STRUCTURE
# ----------------------------
def init(data, bot, symbol):
    if bot not in data:
        data[bot] = {}

    if symbol not in data[bot]:
        data[bot][symbol] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "balance": 500.0,
            "equity_curve": [],
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "max_drawdown": 0.0,
            "peak_balance": 500.0,
            "last_update": None
        }


# ----------------------------
# UPDATE TRADE
# ----------------------------
def update_trade(data, bot, symbol, pnl):
    init(data, bot, symbol)

    s = data[bot][symbol]

    s["trades"] += 1
    s["pnl"] += pnl
    s["balance"] += pnl

    # win/loss tracking
    if pnl > 0:
        s["wins"] += 1
        s["largest_win"] = max(s["largest_win"], pnl)
    else:
        s["losses"] += 1
        s["largest_loss"] = min(s["largest_loss"], pnl)

    # equity curve
    s["equity_curve"].append(s["balance"])

    # peak tracking
    if s["balance"] > s["peak_balance"]:
        s["peak_balance"] = s["balance"]

    # drawdown
    drawdown = s["peak_balance"] - s["balance"]
    s["max_drawdown"] = max(s["max_drawdown"], drawdown)

    s["last_update"] = str(datetime.utcnow())


# ----------------------------
# METRICS CALC
# ----------------------------
def compute_metrics(symbol_data):
    trades = symbol_data["trades"]

    return {
        "trades": trades,
        "win_rate": (symbol_data["wins"] / trades * 100) if trades > 0 else 0,
        "profit": round(symbol_data["pnl"], 2),
        "balance": round(symbol_data["balance"], 2),
        "avg_win": round(symbol_data["largest_win"], 2),
        "avg_loss": round(symbol_data["largest_loss"], 2),
        "max_drawdown": round(symbol_data["max_drawdown"], 2),
    }
