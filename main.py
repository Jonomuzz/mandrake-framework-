import time
import traceback

from core.data import get_klines
from core.notifications import send_telegram
from core.execution import process_trade, check_positions
from core.accounting import build_summary

from strategies.mean_reversion import get_signal as mean_reversion_signal
from strategies.trend import get_signal as trend_signal
from strategies.momentum import get_signal as momentum_signal
from strategies.breakout import get_signal as breakout_signal


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "LTCUSDT",
    "ATOMUSDT"
]


INTERVAL = "1m"
LIMIT = 100


last_signals = {}

    run()
