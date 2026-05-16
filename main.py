import time
import requests
import pandas as pd

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
from core.strategy_registry import get_strategy

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
        return "trend_strength_crossover"

    if vol_ratio > 0.01:
        return "breakout"

    if slope > 0 and vol_ratio < 0.006:
        return "momentum"

    return "mean_reversion"


# =========================
# SIGNAL ENGINE (NEW)
# =========================
def get_signal(df, strategy_name):

    strategy = get_strategy(strategy_name)

    if strategy is None:
        return None

    df = strategy.calculate_indicators(df)

    return strategy.check_signal(df)


# =========================
# MAIN LOOP
# =========================
def run():

    print("🚀 STRATEGY REGISTRY ENGINE STARTED")
    send_telegram("🚀 STRATEGY REGISTRY ENGINE STARTED")

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

                # =========================
                # SAFETY FILTERS
                # =========================
                if is_disabled(strategy):
                    continue

                if correlation_block(symbol):
                    continue

                # regime weighting
                if strategy in bias and bias[strategy] < 0.7:
                    continue

                signal = get_signal(df, strategy)
                price = df["close"].iloc[-1]

                print(f"[{symbol}] Regime={regime} Strategy={strategy} Signal={signal}")

                # =========================
                # EXECUTION
                # =========================
                if signal:
                    update_correlation(symbol)
                    handle_trade(symbol, signal, price, strategy)

            except Exception as e:
                print(f"Error {symbol}: {e}")

        update_capital_rotation()

        time.sleep(SLEEP)


if __name__ == "__main__":
    run()
