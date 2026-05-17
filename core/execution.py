from core.position_manager import (
    has_position,
    open_position,
    close_position,
    get_position
)

from core.notifications import send_telegram
from core.accounting import record_trade


TAKE_PROFIT = 2.0
STOP_LOSS = -1.0


def process_trade(
    symbol,
    strategy,
    signal,
    price
):

    # =========================
    # OPEN POSITION
    # =========================
    if signal == "BUY":

        if not has_position(symbol):

            open_position(
                symbol,
                "LONG",
                price,
                strategy
            )

            send_telegram(
                f"🟢 OPEN LONG {symbol}\n"
                f"Strategy: {strategy}\n"
                f"Entry: {price}"
            )

        return

    # =========================
    # MANAGE POSITION
    # =========================
    if has_position(symbol):

        position = get_position(symbol)

        entry = position["entry_price"]

        pnl_pct = (
            (price - entry) / entry
        ) * 100

        # =========================
        # TAKE PROFIT
        # =========================
        if pnl_pct >= TAKE_PROFIT:

            send_telegram(
                f"🏆 TAKE PROFIT HIT\n"
                f"{symbol}\n"
                f"PnL: {round(pnl_pct, 2)}%"
            )

            record_trade(pnl_pct)

            close_position(symbol)

            return

        # =========================
        # STOP LOSS
        # =========================
        if pnl_pct <= STOP_LOSS:

            send_telegram(
                f"🛑 STOP LOSS HIT\n"
                f"{symbol}\n"
                f"PnL: {round(pnl_pct, 2)}%"
            )

            record_trade(pnl_pct)

            close_position(symbol)

            return

        # =========================
        # SELL SIGNAL EXIT
        # =========================
        if signal == "SELL":

            send_telegram(
                f"🔴 CLOSE POSITION\n"
                f"{symbol}\n"
                f"PnL: {round(pnl_pct, 2)}%"
            )

            record_trade(pnl_pct)

            close_position(symbol)

            return
