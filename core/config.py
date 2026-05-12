import os

# ================= GENERAL =================
ACTIVE_STRATEGY = os.getenv("ACTIVE_STRATEGY", "trend")

PAIRS = ["BTCUSDT", "BNBUSDT"]
INTERVAL = "1m"
LIMIT = 100
SLEEP = 30

# ================= RISK =================
START_BALANCE_PER_PAIR = 500
RISK_PER_TRADE = 0.10

# ================= TELEGRAM =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("ALERT_CHAT_ID")
