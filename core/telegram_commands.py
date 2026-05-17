from core.notifications import send_telegram
from core.config import RISK_PER_TRADE, RISK_MIN, RISK_MAX

risk_state = {
    "risk_pct": RISK_PER_TRADE
}

frequency_state = {
    "mode": "balanced",
    "paused": False
}


def process_command(text, freq_controller):
    if not text:
        return

    text = text.lower()

    # ================= RISK CONTROL =================
    if text.startswith("/risk"):
        try:
            value = float(text.split(" ")[1])

            # HARD SAFETY LIMIT
            if value < RISK_MIN * 100 or value > RISK_MAX * 100:
                send_telegram(
                    f"❌ Risk must be between "
                    f"{RISK_MIN*100}% and {RISK_MAX*100}%"
                )
                return

            risk_state["risk_pct"] = value / 100
            send_telegram(f"📊 Risk set to {value}%")

        except:
            send_telegram("❌ Invalid risk command. Example: /risk 5")
        return

    # ================= MODE CONTROL =================
    if text.startswith("/mode"):
        mode = text.split(" ")[1]
        freq_controller.set_mode(mode)
        send_telegram(f"📈 Mode set to {mode}")
        return

    # ================= PAUSE =================
    if text == "/pause":
        frequency_state["paused"] = True
        send_telegram("⛔ Trading paused")
        return

    # ================= RESUME =================
    if text == "/resume":
        frequency_state["paused"] = False
        send_telegram("✅ Trading resumed")
        return
