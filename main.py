import time
import os
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)

from core.signal_strength import score_signal
from core.frequency_controller import FrequencyController
from core.signal_activation import SignalActivationLayer
from core.telegram_commands import frequency_state
from core.notifications import send_telegram
from core.config import PAIRS, INTERVAL, LIMIT, SLEEP


# =========================
# INIT SYSTEMS
# =========================
freq_controller = FrequencyController()
activation_layer = SignalActivationLayer()

BASE_URL = "https://api.binance.com/api/v3/klines"


# =========================
# DATA LOADER (FULL OHLCV FIX)
# =========================
def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(BASE_URL, params=params)
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

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float
