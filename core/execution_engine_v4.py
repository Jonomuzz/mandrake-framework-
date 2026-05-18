import numpy as np
from core.risk_engine_v4 import (
    update_equity,
    risk_kill_switch,
    strategy_weight,
    update_strategy
)

positions = {}
cooldowns = {}

MAX_OPEN = 4
COOLDOWN = 3
MAX_EXPOSURE = 0.35


# =========================
# HELPERS
# =========================

def atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    tr = np.maximum(high_low, np.maximum(high_close, low_close))

    return tr.rolling(period).mean().iloc[-1]


def exposure():
    return sum(p["size"] for p in positions.values() if p["open"])


def cooldown_tick():
    for s in list(cooldowns.keys()):
        cooldowns[s] -= 1
        if cooldowns[s] <= 0:
            del cooldowns[s]


def set_cd(symbol):
    cooldowns[symbol] = COOLDOWN


# =========================
# EXECUTION CORE
# =========================

def process_trade(symbol, signal, price, df, strategy="trend", balance=500):

    if risk_kill_switch():
        print("🛑 KILL SWITCH ACTIVE (DRAWDOWN LIMIT)")
        return

    if signal is None:
        return

    if len(positions) >= MAX_OPEN:
        return

    if symbol in cooldowns:
        return

    vol = atr(df)

    if np.isnan(vol):
        return

    weight = strategy_weight(strategy)

    risk_amount = (balance * 0.02) * weight  # base 2% scaled

    # exposure cap
    if exposure() + risk_amount > balance * MAX_EXPOSURE:
        return

    sl_dist = vol * 1.2
    tp_dist = vol * 1.8

    # =========================
    # OPEN POSITION
    # =========================
    if symbol not in positions or not positions[symbol]["open"]:

        if signal == "BUY":
            sl = price - sl_dist
            tp = price + tp_dist
        else:
            sl = price + sl_dist
            tp = price - tp_dist

        positions[symbol] = {
            "side": signal,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "size": risk_amount,
            "strategy": strategy,
            "open": True
        }

        print(f"🟢 OPEN {signal} {symbol} @ {price} | SL {sl:.2f} TP {tp:.2f}")
        return

    pos = positions[symbol]

    # =========================
    # EXIT LOGIC
    # =========================

    pnl = 0

    if pos["side"] == "BUY":
        pnl = price - pos["entry"]
        hit_sl = price <= pos["sl"]
        hit_tp = price >= pos["tp"]
    else:
        pnl = pos["entry"] - price
        hit_sl = price >= pos["sl"]
        hit_tp = price <= pos["tp"]

    if hit_sl or hit_tp or signal != pos["side"]:

        win = pnl > 0

        update_equity(pnl)
        update_strategy(strategy, win)

        print(f"🔴 CLOSE {symbol} | PnL {pnl:.4f}")

        positions[symbol]["open"] = False

        set_cd(symbol)
