import json
import os

DATA_FILE = "storage/metrics.json"


# =========================
# LOAD / SAVE
# =========================

def load_state():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    os.makedirs("storage", exist_ok=True)

    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=4)


# =========================
# RISK ENGINE (FIXED MISSING IMPORT)
# =========================

def get_risk_amount(balance, risk_percent=10):
    """
    Calculates position size based on account balance
    """
    try:
        risk = float(balance) * (float(risk_percent) / 100.0)
        return round(risk, 2)
    except:
        return 0.0


# =========================
# UPDATE TRADE RESULTS
# =========================

def update_trade(symbol, pnl, win):

    state = load_state()

    if symbol not in state:
        state[symbol] = {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0
        }

    state[symbol]["trades"] += 1
    state[symbol]["pnl"] += pnl

    if win:
        state[symbol]["wins"] += 1
    else:
        state[symbol]["losses"] += 1

    save_state(state)


# =========================
# SUMMARY REPORT
# =========================

def build_summary():

    state = load_state()

    lines = []

    total_trades = 0
    total_pnl = 0.0
    total_wins = 0

    for symbol, data in state.items():

        trades = data.get("trades", 0)
        wins = data.get("wins", 0)
        pnl = data.get("pnl", 0.0)

        if trades == 0:
            continue

        win_rate = (wins / trades) * 100

        lines.append(
            f"{symbol} | Trades: {trades} | Win Rate: {win_rate:.1f}% | PnL: {pnl:.2f}"
        )

        total_trades += trades
        total_pnl += pnl
        total_wins += wins

    if total_trades == 0:
        return "No trades yet."

    total_win_rate = (total_wins / total_trades) * 100

    lines.append("")
    lines.append(
        f"TOTAL | Trades: {total_trades} | Win Rate: {total_win_rate:.1f}% | PnL: {total_pnl:.2f}"
    )

    return "\n".join(lines)
