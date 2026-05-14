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
# MARKET SETTINGS
# =========================
PAIRS = [
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

# =========================
# TIMEFRAME
# =========================
INTERVAL = os.getenv("INTERVAL", "1m")

# =========================
# DATA SETTINGS
# =========================
LIMIT = 300

# =========================
# LOOP SETTINGS
# =========================
SLEEP = 60

# =========================
# RISK SETTINGS
# =========================
RISK_PER_TRADE = 0.10

# =========================
# PAPER TRADING
# =========================
START_BALANCE_PER_PAIR = 500
