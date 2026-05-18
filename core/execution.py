from core.accounting import update_trade, get_risk_amount


# =========================
# SIMPLE POSITION STORE
# =========================

positions = {}


# =========================
# OPEN / CLOSE LOGIC
# =========================

def process_trade(symbol, signal, price, balance=500, risk_pct=10):

    if signal is None:
        return

    risk_amount = get_risk_amount(balance, risk_pct)

    if symbol not in positions:
        positions[symbol] = None

    # =========================
    # OPEN POSITION
    # =========================
    if positions[symbol] is None:

        positions[symbol] = {
            "side": signal,
            "entry": price,
            "size": risk_amount
        }

        print(f"🟢 OPEN {signal} {symbol} @ {price}")

        return

    # =========================
    # CLOSE CONDITION
    # =========================
    pos = positions[symbol]

    if pos["side"] != signal:

        pnl = 0

        if pos["side"] == "BUY":
            pnl = price - pos["entry"]
        else:
            pnl = pos["entry"] - price

        win = pnl > 0

        update_trade(symbol, pnl, win)

        print(f"🔴 CLOSE {symbol} | PnL: {pnl:.2f}")

        positions[symbol] = None


# =========================
# POSITION CHECK (SAFE HOOK)
# =========================

def check_positions(symbol, price):
    """
    Can be extended later for SL/TP/trailing stops
    Currently just keeps structure stable
    """

    if symbol not in positions:
        positions[symbol] = None

    return positions[symbol]
