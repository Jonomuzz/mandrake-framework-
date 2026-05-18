from core.position_manager import (
    has_position,
    open_position,
    close_position,
    get_position
)

from core.accounting import (
    get_risk_amount,
    record_trade
)

from core.notifications import send_telegram


TP_PERCENT = 0.015
SL_PERCENT = 0.01



def process_trade(symbol, signal, current_price):

    if signal is None:
        return

    # BLOCK DUPLICATES
    if has_position(symbol):
        return

    risk_amount = get_risk_amount(symbol, 10)

    open_position(
        symbol=symbol,
        side=signal,
        entry_price=current_price,
        size=risk_amount
        close_position(symbol)
