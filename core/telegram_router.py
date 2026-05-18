from core.control_panel import (
    get_status,
    get_positions,
    get_balance,
    pause_trading,
    resume_trading,
    reset_system,
    export_taxes
)


def handle_command(text):

    text = text.lower().strip()

    if text == "/status":
        return get_status()

    if text == "/positions":
        return get_positions()

    if text == "/balance":
        return get_balance()

    if text == "/pause":
        return pause_trading()

    if text == "/resume":
        return resume_trading()

    if text == "/reset":
        return reset_system()

    if text == "/taxes":
        return export_taxes()

    return None
