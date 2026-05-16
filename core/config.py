import os

# =========================
# ACTIVE STRATEGY
# =========================
ACTIVE_STRATEGY = os.getenv("ACTIVE_STRATEGY", "trend")

# =========================
# TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALERT_CHAT_ID = os.getenv("ALERT_CHAT_ID")

# =========================
# MARKET
# =========================
PAIRS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT",
    "XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","ATOMUSDT"
]

INTERVAL = os.getenv("INTERVAL", "1m")
LIMIT = 300
SLEEP = 60

# =========================
# RISK BASE
# =========================
RISK_PER_TRADE = 0.10

BASE_RISK = {
    "trend_ma_crossover": 0.15,
    "mean_reversion": 0.10,
    "breakout": 0.12,
    "momentum": 0.08,
    "kst": 0.05
}

risk_multiplier = {}

START_BALANCE_PER_PAIR = 500


# =========================
# RISK ENGINE
# =========================
from core.metrics import get_allocation

def get_risk(strategy):

    base = BASE_RISK.get(strategy, 0.10)
    mult = risk_multiplier.get(strategy, 1.0)

    allocation = get_allocation(strategy)

    return round(base * mult * allocation, 3)


def update_risk(strategy, pnl):

    if strategy not in risk_multiplier:
        risk_multiplier[strategy] = 1.0

    if pnl > 0:
        risk_multiplier[strategy] *= 1.02
    else:
        risk_multiplier[strategy] *= 0.98

    risk_multiplier[strategy] = max(0.5, min(1.5, risk_multiplier[strategy]))
