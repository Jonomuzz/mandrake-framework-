import os

# =========================
# ACTIVE SETTINGS
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
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT",
    "LINKUSDT", "MATICUSDT", "LTCUSDT", "ATOMUSDT"
]

INTERVAL = os.getenv("INTERVAL", "1m")
LIMIT = 300
SLEEP = 60

# =========================
# RISK CONTROL (DEFAULT)
# =========================
RISK_PER_TRADE = 0.05  # 5% default

RISK_MIN = 0.01   # 1%
RISK_MAX = 0.15   # 15%

# =========================
# CAPITAL
# =========================
START_BALANCE_PER_PAIR = 500
