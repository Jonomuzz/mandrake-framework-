from core.position_manager import is_open, open_position, close_position
from core.portfolio import update_balance
from core.telegram import send_telegram


entry_prices = {}


def execute(symbol, signal, price, size_pct=0.10):
    # -------------------------
    # OPEN TRADE
    # -------------------------
    if signal == "BUY" and not is_open(symbol):
        open_position(symbol)
        entry_prices[symbol] = price

        send_telegram(f"🟢 OPEN BUY {symbol} @ {price}")
        return

    # -------------------------
    # CLOSE TRADE
    # -------------------------
    if signal == "SELL" and is_open(symbol):
        entry = entry_prices[symbol]
        pnl_pct = ((price - entry) / entry) * 100

        trade_size = 500 * size_pct
        pnl_usd = trade_size * (pnl_pct / 100)

        update_balance(symbol, pnl_usd)
        close_position(symbol)

        send_telegram(
            f"🔴 CLOSE {symbol} @ {price}\n"
            f"PnL: {pnl_pct:.2f}% | ${pnl_usd:.2f}"
        )
