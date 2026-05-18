import time
from core.data import get_klines

from strategies.trend import get_signal as trend_signal
from strategies.mean_reversion import get_signal as mr_signal
from strategies.breakout import get_signal as breakout_signal
from strategies.momentum import get_signal as momentum_signal

from core.execution_engine_v3 import process_trade, tick_cooldowns


SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100

BALANCE = 500
RISK_PCT = 10


def select_strategy(df):

    # simple router (you can upgrade later)
    return {
        "trend": trend_signal,
        "mean_reversion": mr_signal,
        "breakout": breakout_signal,
        "momentum": momentum_signal
    }


def run():

    print("🚀 FULL V3 EXECUTION ENGINE STARTED")

    while True:

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, INTERVAL, LIMIT)

                strategies = select_strategy(df)

                for name, strat in strategies.items():

                    signal = strat(df)

                    if signal:
                        price = df.iloc[-1]["close"]

                        process_trade(
                            symbol=symbol,
                            signal=signal,
                            price=price,
                            balance=BALANCE,
                            risk_pct=RISK_PCT
                        )

            except Exception as e:
                print(f"Error {symbol}: {e}")

        tick_cooldowns()
        print("Cycle complete...")
        time.sleep(60)


if __name__ == "__main__":
    run()
