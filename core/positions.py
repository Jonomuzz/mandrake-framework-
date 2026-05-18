from datetime import datetime

POSITIONS = []


def open_position(symbol, side, entry_price, qty, sl, tp, strategy):
    position = {
        "id": f"{symbol}-{datetime.utcnow().timestamp()}",
        "symbol": symbol,
        "side": side,
        "entry": entry_price,
        "qty": qty,
        "sl": sl,
        "tp": tp,
        "strategy": strategy,
        "status": "OPEN",
        "open_time": datetime.utcnow(),
        "close_time": None,
        "exit_price": None,
        "pnl": 0.0
    }

    POSITIONS.append(position)
    return position


def close_position(position, exit_price, reason):
    position["exit_price"] = exit_price
    position["close_time"] = datetime.utcnow()
    position["status"] = "CLOSED"

    if position["side"] == "BUY":
        position["pnl"] = (exit_price - position["entry"]) * position["qty"]
    else:
        position["pnl"] = (position["entry"] - exit_price) * position["qty"]

    position["close_reason"] = reason
    return position


def get_open_positions(symbol=None):
    if symbol:
        return [p for p in POSITIONS if p["status"] == "OPEN" and p["symbol"] == symbol]
    return [p for p in POSITIONS if p["status"] == "OPEN"]


def get_all_positions():
    return POSITIONS
