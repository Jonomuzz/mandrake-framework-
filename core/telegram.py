import requests

from core.config import TELEGRAM_TOKEN, ALERT_CHAT_ID


def send_telegram(message):

    if not TELEGRAM_TOKEN or not ALERT_CHAT_ID:
        print("Telegram not configured properly")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": ALERT_CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")
