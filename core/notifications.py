import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    print("📨 Attempting Telegram send:", message)

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        }, timeout=10)

        print("📨 Telegram response:", r.status_code, r.text)

    except Exception as e:
        print("❌ Telegram exception:", e)
