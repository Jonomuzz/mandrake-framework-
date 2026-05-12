import requests

from core.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured properly")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"Telegram failed: {response.text}")

    except Exception as e:
        print(f"Telegram error: {e}")
