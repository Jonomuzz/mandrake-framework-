from core.lifecycle_engine_v5 import positions, trade_history
from core.portfolio_v5 import state
import pandas as pd
import os

TRADING_PAUSED = False


# =========================
# STATUS
# =========================
def get_status():
    total_trades = len(trade_history)
    win = state["wins"]
    loss = state["losses"]
    wr = (win / total_trades * 100) if total_trades > 0 else 0

    return (
        f"📊 STATUS\n"
        f"Balance: ${state['balance']:.2f}\n"
        f"Trades: {total_trades}\n"
        f"Win Rate: {wr:.2f}%\n"
        f"Wins: {win} | Losses: {loss}"
    )


# =========================
# POSITIONS
# =========================
def get_positions():
    if not positions:
        return "No open positions."

    lines = []
    for s, p in positions.items():
        if p["open"]:
            lines.append(
                f"{s} | {p['side']} | Entry: {p['entry']:.4f} | SL: {p['sl']:.4f} | TP: {p['tp']:.4f}"
            )

    return "\n".join(lines) if lines else "No open positions."


# =========================
# BALANCE
# =========================
def get_balance():
    return f"💰 Balance: ${state['balance']:.2f}"


# =========================
# PAUSE / RESUME
# =========================
def pause_trading():
    global TRADING_PAUSED
    TRADING_PAUSED = True
    return "⛔ Trading paused"


def resume_trading():
    global TRADING_PAUSED
    TRADING_PAUSED = False
    return "▶ Trading resumed"


def is_paused():
    return TRADING_PAUSED


# =========================
# RESET
# =========================
def reset_system():
    positions.clear()
    trade_history.clear()
    state["balance"] = 500
    state["wins"] = 0
    state["losses"] = 0
    return "🔄 System reset complete"


# =========================
# TAX EXPORT
# =========================
def export_taxes():
    if not trade_history:
        return "No trades to export."

    df = pd.DataFrame(trade_history)

    path = "/mnt/data/trade_history.csv"
    df.to_csv(path, index=False)

    return f"📁 Tax file exported: {path}"
