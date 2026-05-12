from core.execution import stats
from core.telegram import send_telegram



def send_metrics(pairs):
    total_profit = 0
    total_balance = 0
    total_trades = 0

    message = "📊 PERFORMANCE SUMMARY\n\n"

    for pair in pairs:
        s = stats[pair]

        win_rate = (
            (s["wins"] / s["trades"] * 100)
            if s["trades"] > 0 else 0
        )

        message += (
            f"{pair}\n"
            f"Trades: {s['trades']}\n"
            f"Win Rate: {round(win_rate, 1)}%\n"
            f"Profit: {round(s['profit_pct'], 2)}%\n"
            f"Balance: ${round(s['balance'], 2)}\n\n"
        )

        total_profit += s["profit_usd"]
        total_balance += s["balance"]
        total_trades += s["trades"]

    message += (
        f"TOTAL\n"
        f"Trades: {total_trades}\n"
        f"Profit: ${round(total_profit, 2)}\n"
        f"Balance: ${round(total_balance, 2)}"
    )

    send_telegram(message)
