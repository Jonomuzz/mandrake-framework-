import requests
from core.config import TELEGRAM_TOKEN, ALERT_CHAT_ID


def send_telegram(message):
    print("📨 Attempting Telegram send:", message)

    # Debug visibility (helps you avoid silent failures)
    print("🔍 TOKEN LOADED:", bool(TELEGRAM_TOKEN))
    print("🔍 CHAT ID LOADED:", bool(ALERT_CHAT_ID))

    if not TELEGRAM_TOKEN or not ALERT_CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or ALERT_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        r = requests.post(
            url,
            data={
                "chat_id": ALERT_CHAT_ID,
                "text": message
            },
            timeout=10
        )

        print("📨 Telegram response:", r.status_code, r.text)

    except Exception as e:
        print("❌ Telegram exception:", e)
