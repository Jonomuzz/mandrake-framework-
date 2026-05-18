import time

# =========================
# GLOBAL POSITION STATE
# =========================

positions = {}

COOLDOWN = {}  # prevents rapid re-entry per symbol
COOLDOWN_CYCLES = 3  # adjust if needed


# =========================
# POSITION HELPERS
# =========================

def is_in_cooldown(symbol):
    if symbol not in COOLDOWN:
        return False
    return COOLDOWN[symbol] > 0


def tick_cooldowns():
    for s in list(COOLDOWN.keys()):
        COOLDOWN[s] -= 1
        if COOLDOWN[s] <= 0:
            del COOLDOWN[s]


def set_cooldown(symbol):
    COOLDOWN[symbol] = COOLDOWN_CYCLES


# =========================
# MAIN EXECUTION LOGIC
# =========================

def process_signal(symbol, signal, price, risk_pct=10, balance=500):
    """
    V2 Position-State Execution Engine
    """

    if signal is None:
        return None

    # initialize symbol state
    if symbol not in positions:
        positions[symbol] = {
            "side": None,
            "entry": None,
            "open": False
        }

    pos = positions[symbol]

    # =========================
    # COOLDOWN CHECK
    # =========================
    if is_in_cooldown(symbol):
        return None

    # =========================
    # NO POSITION → OPEN NEW
    # =========================
    if not pos["open"]:
        positions[symbol] = {
            "side": signal,
            "entry": price,
            "open": True
        }

        print(f"🟢 OPEN {signal} {symbol} @ {price}")

        return f"OPEN {signal}"

    # =========================
    # SAME SIGNAL → DO NOTHING
    # =========================
    if pos["side"] == signal:
        return None

    # =========================
    # OPPOSITE SIGNAL → CLOSE + REVERSE
    # =========================

    entry = pos["entry"]
    side = pos["side"]

    if side == "BUY":
        pnl = price - entry
    else:
        pnl = entry - price

    print(f"🔴 CLOSE {symbol} | PnL: {pnl:.4f}")

    # RESET POSITION
    positions[symbol] = {
        "side": signal,
        "entry": price,
        "open": True
    }

    set_cooldown(symbol)

    print(f"🔄 REVERSE {symbol} → {signal} @ {price}")

    return f"CLOSE+REVERSE {signal}"


# =========================
# OPTIONAL POSITION VIEW
# =========================

def get_position(symbol):
    return positions.get(symbol, None)
