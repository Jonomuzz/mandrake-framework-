import json
import os


METRICS_FILE = "storage/metrics.json"


DEFAULT_METRICS = {
    "total_trades": 0,
    "wins": 0,
    "losses": 0,
    "gross_profit": 0,
    "gross_loss": 0,
    "largest_win": 0,
    "largest_loss": 0,
    "consecutive_losses": 0,
    "max_consecutive_losses": 0,
    "max_drawdown": 0,
    "peak_balance": 0,
    "current_drawdown": 0,
    "trade_history": []
}


# =========================
# LOAD METRICS
# =========================
def load_metrics():

    if not os.path.exists(METRICS_FILE):
        return DEFAULT_METRICS.copy()

    with open(METRICS_FILE, "r") as f:
        return json.load(f)


# =========================
# SAVE METRICS
# =========================
def save_metrics(metrics):

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)


# =========================
# UPDATE METRICS
# =========================
def update_metrics(metrics, pnl, balance):

    metrics["total_trades"] += 1

    metrics["trade_history"].append(pnl)

    # =========================
    # WIN / LOSS
    # =========================
    if pnl > 0:

        metrics["wins"] += 1
        metrics["gross_profit"] += pnl
        metrics["consecutive_losses"] = 0

        if pnl > metrics["largest_win"]:
            metrics["largest_win"] = pnl

    else:

        metrics["losses"] += 1
        metrics["gross_loss"] += abs(pnl)
        metrics["consecutive_losses"] += 1

        if abs(pnl) > metrics["largest_loss"]:
            metrics["largest_loss"] = abs(pnl)
    }
