from collections import defaultdict
from core.config import RISK_PER_TRADE, START_BALANCE_PER_PAIR
from core.telegram import send_telegram

# =========================
# POSITION STATE
# =========================
positions = {}
entry_prices = {}

# =========================
# PER-STRATEGY STATS (FIX)
# =========================
stats = defaultdict(lambda: {
    "wins": 0,
    "losses": 0,
    "trades": 0,
    "profit_pct": 0,
    "profit_usd": 0,
    "balance": START_BALANCE_PER_PAIR
})


def initialize_pairs(pairs):
    for pair in pairs:
        positions[pair] = None
        entry_prices[pair] = 0


def handle_trade(pair, signal, price, strategy):
    """
    IMPORTANT FIX:
    Now strategy is tracked per trade
    """

    # =========================
    # BUY
    # =========================
    if signal == "BUY" and positions[pair] is None:

        positions[pair] = {
            "side": "LONG",
            "strategy": strategy
        }

        entry_prices[pair] = price
        stats[pair]["trades"] += 1

        msg = f"🟢 BUY {pair} | STRATEGY={strategy} @ {price}"
        print(msg)
        send_telegram(msg)

    # =========================
    # SELL
    # =========================
    elif signal == "SELL" and positions[pair] is not None:

        pos = positions[pair]

        pnl_pct = ((price - entry_prices[pair]) / entry_prices[pair]) * 100

        trade_size = stats[pair]["balance"] * RISK_PER_TRADE
        pnl_usd = trade_size * (pnl_pct / 100)

        stats[pair]["profit_pct"] += pnl_pct
        stats[pair]["profit_usd"] += pnl_usd
        stats[pair]["balance"] += pnl_usd

        if pnl_usd > 0:
            stats[pair]["wins"] += 1
        else:
            stats[pair]["losses"] += 1

        msg = (
            f"🔴 SELL {pair} | STRATEGY={pos['strategy']}\n"
            f"PnL: {round(pnl_pct, 3)}% | ${round(pnl_usd, 2)}\n"
            f"Wins: {stats[pair]['wins']} | Losses: {stats[pair]['losses']}\n"
            f"Balance: ${round(stats[pair]['balance'], 2)}"
        )

        print(msg)
        send_telegram(msg)

        positions[pair] = None
        entry_prices[pair] = 0
