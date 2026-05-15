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
    # WIN
    # =========================
    if pnl > 0:

        metrics["wins"] += 1
        metrics["gross_profit"] += pnl

        metrics["consecutive_losses"] = 0

        if pnl > metrics["largest_win"]:
            metrics["largest_win"] = pnl

    # =========================
    # LOSS
    # =========================
    else:

        metrics["losses"] += 1
        metrics["gross_loss"] += abs(pnl)

        metrics["consecutive_losses"] += 1

        if abs(pnl) > metrics["largest_loss"]:
            metrics["largest_loss"] = abs(pnl)

    # =========================
    # MAX CONSECUTIVE LOSSES
    # =========================
    if (
        metrics["consecutive_losses"]
        > metrics["max_consecutive_losses"]
    ):
        metrics["max_consecutive_losses"] = (
            metrics["consecutive_losses"]
        )

    # =========================
    # PEAK BALANCE
    # =========================
    if balance > metrics["peak_balance"]:
        metrics["peak_balance"] = balance

    # =========================
    # DRAWDOWN
    # =========================
    drawdown = (
        metrics["peak_balance"] - balance
    )

    metrics["current_drawdown"] = drawdown

    if drawdown > metrics["max_drawdown"]:
        metrics["max_drawdown"] = drawdown

    save_metrics(metrics)


# =========================
# ADVANCED METRICS
# =========================
def calculate_advanced_metrics(metrics):

    total_trades = metrics["total_trades"]

    if total_trades == 0:
        return {
            "win_rate": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "profit_factor": 0,
            "max_drawdown": 0,
            "max_consecutive_losses": 0,
            "largest_win": 0,
            "largest_loss": 0
        }

    # =========================
    # WIN RATE
    # =========================
    win_rate = (
        metrics["wins"] / total_trades
    ) * 100

    # =========================
    # AVERAGE WIN
    # =========================
    avg_win = 0

    if metrics["wins"] > 0:
        avg_win = (
            metrics["gross_profit"]
            / metrics["wins"]
        )

    # =========================
    # AVERAGE LOSS
    # =========================
    avg_loss = 0

    if metrics["losses"] > 0:
        avg_loss = (
            metrics["gross_loss"]
            / metrics["losses"]
        )

    # =========================
    # PROFIT FACTOR
    # =========================
    profit_factor = 0

    if metrics["gross_loss"] > 0:
        profit_factor = (
            metrics["gross_profit"]
            / metrics["gross_loss"]
        )

    return {
        "win_rate": round(win_rate, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": round(
            metrics["max_drawdown"], 2
        ),
        "max_consecutive_losses": metrics[
            "max_consecutive_losses"
        ],
        "largest_win": round(
            metrics["largest_win"], 2
        ),
        "largest_loss": round(
            metrics["largest_loss"], 2
        )
    }
