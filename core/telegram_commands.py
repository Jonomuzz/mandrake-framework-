from core.config import RISK_PER_TRADE
from core.notifications import send_telegram

risk_state = {
    "risk_pct": RISK_PER_TRADE
}

frequency_state = {
    "mode": "balanced"
}


def process_command(text, freq_controller):
    """
    Telegram command handler
    """

    if not text:
        return None

    text = text.lower()

    # ================= RISK CONTROL =================
    if text.startswith("/risk"):
        try:
            value = float(text.split(" ")[1])
            risk_state["risk_pct"] = value / 100
            send_telegram(f"📊 Risk set to {value}%")
        except:
            send_telegram("Invalid risk command")
        return

    # ================= MODE CONTROL =================
    if text.startswith("/mode"):
        mode = text.split(" ")[1]
        freq_controller.set_mode(mode)
        send_telegram(f"📈 Mode set to {mode}")
        return

    # ================= PAUSE / RESUME =================
    if text == "/pause":
        frequency_state["paused"] = True
        send_telegram("⛔ Trading paused")
        return

    if text == "/resume":
        frequency_state["paused"] = False
        send_telegram("✅ Trading resumed")
        return
