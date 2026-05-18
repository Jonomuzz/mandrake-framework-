import time

from core.data import get_klines

from strategies.trend import get_signal as trend_signal
from strategies.mean_reversion import get_signal as mr_signal
from strategies.breakout import get_signal as breakout_signal
from strategies.momentum import get_signal as momentum_signal

from core.execution_engine_v4 import process_trade, cooldown_tick


SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

BALANCE = 500
INTERVAL = "1m"
LIMIT = 100


def strategies():
    return {
        "trend": trend_signal,
        "mean_reversion": mr_signal,
        "breakout": breakout_signal,
        "momentum": momentum_signal
    }


def run():

    print("🚀 EXECUTION ENGINE V4 STARTED")

    while True:

        for symbol in SYMBOLS:

            try:
                df = get_klines(symbol, INTERVAL, LIMIT)
                price = df.iloc[-1]["close"]

                strat_map = strategies()

                for name, strat in strat_map.items():

                    signal = strat(df)

                    process_trade(
                        symbol=symbol,
                        signal=signal,
                        price=price,
                        df=df,
                        strategy=name,
                        balance=BALANCE
                    )

            except Exception as e:
                print(f"Error {symbol}: {e}")

        cooldown_tick()
        print("Cycle complete...")
        time.sleep(60)


if __name__ == "__main__":
    run()
