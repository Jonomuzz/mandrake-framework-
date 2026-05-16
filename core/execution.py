from collections import defaultdict
from core.config import RISK_PER_TRADE, START_BALANCE_PER_PAIR
from core.telegram import send_telegram
from core.metrics import update_strategy_metrics

positions = {}
entry_prices = {}

stats = defaultdict(lambda: {
    "wins": 0,
    "losses": 0,
    "trades": 0,
    "profit_pct": 0,
    "profit_usd": 0,
    "balance": START_BALANCE_PER_PAIR
})


def initialize_pairs(pairs):
    for p in pairs:
        positions[p] = None
        entry_prices[p] = 0


def handle_trade(pair, signal, price, strategy):

    # ================= BUY =================
    if signal == "BUY" and positions[pair] is None:

        positions[pair] = {
            "side": "LONG",
            "strategy": strategy
        }

        entry_prices[pair] = price
        stats[pair]["trades"] += 1

        send_telegram(f"🟢 BUY {pair} | {strategy} @ {price}")


    # ================= SELL =================
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

        update_strategy_metrics(strategy, pnl_usd)

        msg = (
            f"🔴 SELL {pair} | {strategy}\n"
            f"PnL: {pnl_pct:.2f}% | ${pnl_usd:.2f}\n"
            f"Balance: ${stats[pair]['balance']:.2f}"
        )

        send_telegram(msg)

        positions[pair] = None
        entry_prices[pair] = 0
