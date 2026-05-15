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


    }
