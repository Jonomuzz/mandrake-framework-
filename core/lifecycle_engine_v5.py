import uuid

positions = {}
trade_history = []

cooldowns = {}

COOLDOWN_CYCLES = 3


# =========================
# POSITION HELPERS
# =========================

def is_open(symbol):
    return symbol in positions and positions[symbol]["open"]


def set_cooldown(symbol):
    cooldowns[symbol] = COOLDOWN_CYCLES


def tick_cooldowns():
    for s in list(cooldowns.keys()):
        cooldowns[s] -= 1
        if cooldowns[s] <= 0:
            del cooldowns[s]


# =========================
# OPEN TRADE
# =========================

def open_trade(symbol, side, price, sl, tp, size, strategy):

    if is_open(symbol):
        return None

    trade_id = str(uuid.uuid4())[:8]

    positions[symbol] = {
        "id": trade_id,
        "symbol": symbol,
        "side": side,
        "entry": price,
        "sl": sl,
        "tp": tp,
        "size": size,
        "strategy": strategy,
        "open": True
    }

    print(f"🟢 OPEN {side} {symbol} @ {price} | SL={sl:.4f} TP={tp:.4f}")

    return trade_id


# =========================
# CLOSE TRADE
# =========================

def close_trade(symbol, price, reason="signal"):

    pos = positions.get(symbol)

    if not pos or not pos["open"]:
        return

    entry = pos["entry"]
    side = pos["side"]
    size = pos["size"]

    if side == "BUY":
        pnl = (price - entry) * size
        win = pnl > 0
    else:
        pnl = (entry - price) * size
        win = pnl > 0

    trade = {
        "id": pos["id"],
        "symbol": symbol,
        "side": side,
        "entry": entry,
        "exit": price,
        "pnl": pnl,
        "win": win,
        "strategy": pos["strategy"],
        "reason": reason
    }

    trade_history.append(trade)

    positions[symbol]["open"] = False

    set_cooldown(symbol)

    print(f"🔴 CLOSE {symbol} | PnL={pnl:.4f} | WIN={win} | REASON={reason}")

    return trade


# =========================
# CHECK ACTIVE POSITION
# =========================

def manage_position(symbol, price):

    pos = positions.get(symbol)

    if not pos or not pos["open"]:
        return None

    # SL HIT
    if pos["side"] == "BUY" and price <= pos["sl"]:
        return close_trade(symbol, price, "SL")

    if pos["side"] == "SELL" and price >= pos["sl"]:
        return close_trade(symbol, price, "SL")

    # TP HIT
    if pos["side"] == "BUY" and price >= pos["tp"]:
        return close_trade(symbol, price, "TP")

    if pos["side"] == "SELL" and price <= pos["tp"]:
        return close_trade(symbol, price, "TP")

    return None
