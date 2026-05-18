from core.lifecycle_engine_v5 import trade_history


state = {
    "balance": 500,
    "wins": 0,
    "losses": 0
}


def update_balance(pnl):
    state["balance"] += pnl

    if pnl > 0:
        state["wins"] += 1
    else:
        state["losses"] += 1


def win_rate():
    total = state["wins"] + state["losses"]
    if total == 0:
        return 0
    return state["wins"] / total


def summary():
    total = state["wins"] + state["losses"]

    print("\n📊 PORTFOLIO SUMMARY")
    print(f"Balance: ${state['balance']:.2f}")
    print(f"Trades: {total}")
    print(f"Win Rate: {win_rate()*100:.2f}%")

    return state
