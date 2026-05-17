import time
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)

from core.notifications import send_telegram
from core.execution_engine import process_trade
from core.config import (
    PAIRS,
    INTERVAL,
    LIMIT,
    SLEEP
)

BASE_URL = "https://api.binance.com/api/v3/klines"


# =========================
# DATA
# =========================
def get_klines(symbol):

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(
        BASE_URL,
        params=params
    )

    data = response.json()

    df = pd.DataFrame(data, columns=[
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "qav",
        "num_trades",
        "taker_base_vol",
        "taker_quote_vol",
        "ignore"
    ])

    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:
        df[col] = df[col].astype(float)

    return df


# =========================
# REGIME DETECTOR
# =========================
def select_strategy(df):

    ma20 = (
        df["close"]
        .rolling(20)
        .mean()
    )

    slope = ma20.diff().iloc[-1]

    vol = (
        df["close"]
        .rolling(20)
        .std()
        .iloc[-1]
    )

    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    if abs(slope) > vol * 0.15:
        return "trend"

    if vol_ratio > 0.01:
        return "breakout"

    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


# =========================
# ROUTER
# =========================
def get_signal(df, strategy):

    try:

        if strategy == "trend":
            df = (
                trend_strength_crossover
                .calculate_indicators(df)
            )

            return (
                trend_strength_crossover
                .check_signal(df)
            )

        if strategy == "mean_reversion":
            df = (
                mean_reversion
                .calculate_indicators(df)
            )

            return (
                mean_reversion
                .check_signal(df)
            )

        if strategy == "breakout":
            df = (
                breakout
                .calculate_indicators(df)
            )

            return (
                breakout
                .check_signal(df)
            )

        if strategy == "momentum":
            df = (
                momentum
                .calculate_indicators(df)
            )

            return (
                momentum
                .check_signal(df)
            )

        if strategy == "kst":
            df = (
                kst
                .calculate_indicators(df)
            )

            return (
                kst
                .check_signal(df)
            )

    except Exception as e:
        print(
            f"Strategy error "
            f"({strategy}): {e}"
        )

    return None


# =========================
# MAIN LOOP
# =========================
def run():

    print(
        "🚀 EXECUTION ENGINE V3 STARTED"
    )

    send_telegram(
        "🚀 EXECUTION ENGINE V3 STARTED"
    )

    while True:

        for symbol in PAIRS:

            try:

                df = get_klines(symbol)

                strategy = (
                    select_strategy(df)
                )

                signal = (
                    get_signal(
                        df,
                        strategy
                    )
                )

                price = (
                    df["close"]
                    .iloc[-1]
                )

                print(
                    f"{symbol} | "
                    f"{strategy} | "
                    f"{signal}"
                )

                if signal:

                    process_trade(
                        symbol,
                        strategy,
                        signal,
                        price
                    )

            except Exception as e:

                print(
                    f"Error {symbol}: {e}"
                )

        print("Cycle complete...\n")

        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
