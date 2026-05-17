import json
import os
from datetime import datetime

FILE = "storage/trade_ledger.json"

if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump([], f)


def log_trade(symbol, strategy, side, entry, exit_price, size, pnl):
    with open(FILE, "r") as f:
        data = json.load(f)

    data.append({
        "time": str(datetime.utcnow()),
        "symbol": symbol,
        "strategy": strategy,
        "side": side,
        "entry": entry,
        "exit": exit_price,
        "size": size,
        "pnl": pnl
    })

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_trades():
    with open(FILE, "r") as f:
        return json.load(f)
