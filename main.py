import time

from core.data import get_klines

from strategies.trend import get_signal as trend_signal
from strategies.mean_reversion import get_signal as mr_signal
from strategies.breakout import get_signal as breakout_signal
from strategies.momentum import get_signal as momentum_signal

from core.lifecycle_engine_v5 import (
    open_trade,
    manage_position,
    tick_cooldowns,
    positions
)

from core.portfolio_v5 import update_balance, summary


SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

BALANCE = 500
RISK_PER_TRADE = 0.02  # 2%


def strategies():
    return {
        "trend": trend_signal,
        "mean_reversion": mr_signal,
        "breakout": breakout_signal,
        "momentum": momentum_signal
    }


def process_symbol(symbol, df):

    price = df.iloc[-1]["close"]

    # 1. FIRST manage existing position
    trade = manage_position(symbol, price)

    if trade:
        update_balance(trade["pnl"])

    # 2. If already open → skip new entry
    if symbol in positions and positions[symbol]["open"]:
        return

    # 3. Evaluate strategies
    for name, strat in strategies().items():

        signal = strat(df)

        if not signal:
            continue

        sl = price * (0.998 if signal == "BUY" else 1.002)
        tp = price * (1.003 if signal == "BUY" else 0.997)

        size = BALANCE * RISK_PER_TRADE

        open_trade(
            symbol=symbol,
            side=signal,
            price=price,
            sl=sl,
            tp=tp,
            size=size,
            strategy=name
        )

        break


def run():

    print("🚀 V5 FULL TRADE LIFECYCLE ENGINE STARTED")

    while True:

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, "1m", 100)
                process_symbol(symbol, df)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        tick_cooldowns()

        summary()

        print("Cycle complete...\n")
        time.sleep(60)


if __name__ == "__main__":
    run()
