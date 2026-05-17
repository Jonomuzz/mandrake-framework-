import time
from core.notifications import send_telegram
from core.portfolio import update_portfolio

# =========================
# EXECUTION ENGINE V3
# =========================

OPEN_POSITIONS = {}  # in-memory position tracking


def open_position(symbol, side, price, portfolio):
    """
    Opens a simulated position
    """

    if symbol in OPEN_POSITIONS:
        return None  # already in trade

    position = {
        "symbol": symbol,
        "side": side,
        "entry": price,
        "time": time.time()
    }

    OPEN_POSITIONS[symbol] = position

    send_telegram(f"🟢 OPEN {side} {symbol} @ {price}")
    return position


def close_position(symbol, price, portfolio):
    """
    Closes position and calculates PnL
    """

    if symbol not in OPEN_POSITIONS:
        return None

    position = OPEN_POSITIONS.pop(symbol)

    entry = position["entry"]

    # PnL %
    if position["side"] == "BUY":
        pnl_pct = ((price - entry) / entry) * 100
    else:
        pnl_pct = ((entry - price) / entry) * 100

    update_portfolio(portfolio, symbol, pnl_pct)

    send_telegram(
        f"🔴 CLOSE {symbol}\n"
        f"Entry: {entry}\n"
        f"Exit: {price}\n"
        f"PnL: {round(pnl_pct, 2)}%"
    )

    return pnl_pct


def process_trade(symbol, signal, price, portfolio):
    """
    Main execution handler
    """

    # NO SIGNAL
    if signal is None:
        return

    # OPEN LONG
    if signal == "BUY":
        return open_position(symbol, "BUY", price, portfolio)

    # OPEN SHORT / EXIT LONG
    if signal == "SELL":
        # if position exists → close
        if symbol in OPEN_POSITIONS:
            return close_position(symbol, price, portfolio)

    return None
