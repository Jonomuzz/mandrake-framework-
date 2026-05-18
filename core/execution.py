from core.accounting import update_trade, get_risk_amount


positions = {}


def process_trade(symbol, signal, price, balance=500, risk_pct=10):

    if signal is None:
        return

    risk_amount = get_risk_amount(balance, risk_pct)

    if symbol not in positions:
        positions[symbol] = None

    # OPEN
    if positions[symbol] is None:

        positions[symbol] = {
            "side": signal,
            "entry": price,
            "size": risk_amount
        }

        print(f"🟢 OPEN {signal} {symbol} @ {price}")
        return

    # CLOSE
    pos = positions[symbol]

    if pos["side"] != signal:

        if pos["side"] == "BUY":
            pnl = price - pos["entry"]
        else:
            pnl = pos["entry"] - price

        win = pnl > 0

        update_trade(symbol, pnl, win)

        print(f"🔴 CLOSE {symbol} | PnL: {pnl:.2f}")

        positions[symbol] = None


def check_positions(symbol, price):

    if symbol not in positions:
        positions[symbol] = None

    return positions[symbol]
