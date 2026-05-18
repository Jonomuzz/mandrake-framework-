import time
from core.accounting import update_trade, get_risk_amount

# =========================
# STATE
# =========================

positions = {}
cooldowns = {}

MAX_EXPOSURE = 0.30   # 30% of balance
MAX_OPEN_TRADES = 4
COOLDOWN_CYCLES = 3

# =========================
# HELPERS
# =========================

def in_cooldown(symbol):
    return cooldowns.get(symbol, 0) > 0


def tick_cooldowns():
    for s in list(cooldowns.keys()):
        cooldowns[s] -= 1
        if cooldowns[s] <= 0:
            del cooldowns[s]


def active_positions():
    return [p for p in positions.values() if p["open"]]


def total_exposure():
    return sum(p["size"] for p in active_positions())


def set_cooldown(symbol):
    cooldowns[symbol] = COOLDOWN_CYCLES


# =========================
# MAIN ENGINE
# =========================

def process_trade(symbol, signal, price, balance=500, risk_pct=10):

    if signal is None:
        return

    # -------------------------
    # INIT POSITION
    # -------------------------
    if symbol not in positions:
        positions[symbol] = {
            "side": None,
            "entry": None,
            "size": 0,
            "sl": None,
            "tp": None,
            "open": False
        }

    pos = positions[symbol]

    # -------------------------
    # GLOBAL LIMITS
    # -------------------------
    if len(active_positions()) >= MAX_OPEN_TRADES:
        return

    if in_cooldown(symbol):
        return

    # -------------------------
    # POSITION SIZE
    # -------------------------
    risk_amount = get_risk_amount(balance, risk_pct)

    # exposure cap check
    if total_exposure() + risk_amount > balance * MAX_EXPOSURE:
        return

    # =========================
    # OPEN TRADE
    # =========================
    if not pos["open"]:

        sl = price * 0.998   # 0.2% SL
        tp = price * 1.003   # 0.3% TP

        if signal == "SELL":
            sl = price * 1.002
            tp = price * 0.997

        positions[symbol] = {
            "side": signal,
            "entry": price,
            "size": risk_amount,
            "sl": sl,
            "tp": tp,
            "open": True
        }

        print(f"🟢 OPEN {signal} {symbol} @ {price} | SL={sl} TP={tp}")

        return

    # =========================
    # CHECK EXIT CONDITIONS
    # =========================

    entry = pos["entry"]
    side = pos["side"]

    pnl = 0

    if side == "BUY":
        pnl = price - entry
        hit_sl = price <= pos["sl"]
        hit_tp = price >= pos["tp"]
    else:
        pnl = entry - price
        hit_sl = price >= pos["sl"]
        hit_tp = price <= pos["tp"]

    if hit_sl or hit_tp or signal != side:

        win = pnl > 0

        update_trade(symbol, pnl, win)

        print(f"🔴 CLOSE {symbol} | PnL={pnl:.4f}")

        positions[symbol]["open"] = False

        set_cooldown(symbol)

        return
