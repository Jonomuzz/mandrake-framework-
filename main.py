import time
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_ma_crossover,
    breakout,
    momentum,
    kst
)

from core.config import PAIRS, SLEEP
from core.execution import handle_trade, initialize_pairs
from core.metrics import (
    update_capital_rotation,
    is_disabled,
    update_correlation,
    correlation_block,
    reset_correlation
)

from core.regime import detect_regime, get_regime_bias

from core.telegram import send_telegram

BASE_URL = "https://api.binance.com/api/v3/klines"
INTERVAL = "1m"
LIMIT = 100


# =========================
# DATA
# =========================
def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)
    return df


# =========================
# STRATEGY SELECTOR
# =========================
def select_strategy(df):

    ma20 = df["close"].rolling(20).mean()
    slope = ma20.diff().iloc[-1]
    vol = df["close"].rolling(20).std().iloc[-1]
    price = df["close"].iloc[-1]

    vol_ratio = vol / price

    if abs(slope) > vol * 0.15:
        return "trend_ma_crossover"

    if vol_ratio > 0.01:
        return "breakout"

    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


# =========================
# ROUTER
# =========================
def get_signal(df, strategy):

    if strategy == "trend_ma_crossover":
        df = trend_ma_crossover.calculate_indicators(df)
        return trend_ma_crossover.check_signal(df)

    if strategy == "mean_reversion":
        df = mean_reversion.calculate_indicators(df)
        return mean_reversion.check_signal(df)

    if strategy == "breakout":
        df = breakout.calculate_indicators(df)
        return breakout.check_signal(df)

    if strategy == "momentum":
        df = momentum.calculate_indicators(df)
        return momentum.check_signal(df)

    if strategy == "kst":
        df = kst.calculate_indicators(df)
        return kst.check_signal(df)

    return None


# =========================
# MAIN LOOP
# =========================
def run():

    print("🚀 SWITCHER + REGIME ENGINE STARTED")
    send_telegram("🚀 SWITCHER + REGIME ENGINE STARTED")

    initialize_pairs(PAIRS)

    while True:

        reset_correlation()

        for symbol in PAIRS:

            try:
                df = get_klines(symbol)

                # =========================
                # REGIME ENGINE
                # =========================
                regime = detect_regime(df)
                bias = get_regime_bias()

                strategy = select_strategy(df)

                # regime suppression / weighting
                if strategy in bias:
                    weight = bias[strategy]

                    if weight < 0.7:
                        print(f"[BLOCKED] {symbol} | {strategy} | {regime}")
                        continue

                # safety layers
                if is_disabled(strategy):
                    continue

                if correlation_block(symbol):
                    continue

                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                print(f"[{symbol}] Regime={regime} Strategy={strategy} Signal={signal}")

                if signal:
                    update_correlation(symbol)
                    handle_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        update_capital_rotation()

        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
