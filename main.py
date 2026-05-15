import time

from core.config import ACTIVE_STRATEGY
from core.config import PAIRS
from core.config import SLEEP
from core.config import START_BALANCE_PER_PAIR

from core.data import get_klines
from core.telegram import send_telegram

from core.metrics import (
    load_metrics,
    update_metrics,
    calculate_advanced_metrics
)

# =========================
# STRATEGY LOADER
# =========================
if ACTIVE_STRATEGY == "trend":

    from strategies.trend import (
        calculate_indicators,
        check_signal
    )

elif ACTIVE_STRATEGY == "mean_reversion":

    from strategies.mean_reversion import (
        calculate_indicators,
        check_signal
    )

elif ACTIVE_STRATEGY == "breakout":

    from strategies.breakout import (
        calculate_indicators,
        check_signal
    )

elif ACTIVE_STRATEGY == "momentum":

    from strategies.momentum import (
        calculate_indicators,
        check_signal
    )

elif ACTIVE_STRATEGY == "kst":

    from strategies.kst import (
        calculate_indicators,
        check_signal
    )

else:
    raise Exception(
        f"Unknown strategy: {ACTIVE_STRATEGY}"
    )

# =========================
# PAPER TRADING STATE
# =========================
balances = {}
positions = {}

# =========================
# INITIALIZE
# =========================
for pair in PAIRS:

    balances[pair] = START_BALANCE_PER_PAIR

    positions[pair] = None

# =========================
# METRICS
# =========================
metrics = load_metrics()

# =========================
# STARTUP
# =========================
print("FRAMEWORK BOT RUNNING")

send_telegram(
    f"🤖 Bot Started\n"
    f"Strategy: {ACTIVE_STRATEGY}"
)

# =========================
# MAIN LOOP
# =========================
while True:

    for pair in PAIRS:

        try:

            print(f"Checking {pair}...")

            df = get_klines(pair)

            df = calculate_indicators(df)

            signal = check_signal(df)

            print(f"{pair} signal: {signal}")

            current_price = df.iloc[-1]["close"]

            # =========================
            # OPEN TRADE
            # =========================
            if (
                positions[pair] is None
                and signal is not None
            ):

                positions[pair] = {
                    "side": signal,
                    "entry": current_price
                }

                send_telegram(
                    f"🚀 TRADE OPENED\n\n"
                    f"Strategy: {ACTIVE_STRATEGY}\n"
                    f"Pair: {pair}\n"
                    f"Side: {signal}\n"
                    f"Entry: {round(current_price, 4)}"
                )

            # =========================
            # MANAGE OPEN TRADE
            # =========================
            elif positions[pair] is not None:

                entry_price = (
                    positions[pair]["entry"]
                )

                side = (
                    positions[pair]["side"]
                )

                pnl_pct = 0

                # =========================
                # BUY TRADE
                # =========================
                if side == "BUY":

                    pnl_pct = (
                        current_price
                        - entry_price
                    ) / entry_price

                # =========================
                # SELL TRADE
                # =========================
                elif side == "SELL":

                    pnl_pct = (
                        entry_price
                        - current_price
                    ) / entry_price

                # =========================
                # EXIT CONDITIONS
                # =========================
                TAKE_PROFIT = 0.003
                STOP_LOSS = -0.002

                if (
                    pnl_pct >= TAKE_PROFIT
                    or pnl_pct <= STOP_LOSS
                ):

                    pnl_dollars = (
                        balances[pair]
                        * pnl_pct
                    )

                    balances[pair] += pnl_dollars

                    update_metrics(
                        metrics,
                        pnl_dollars,
                        balances[pair]
                    )

                    advanced = (
                        calculate_advanced_metrics(
                            metrics
                        )
                    )

                    message = (
                        f"✅ TRADE CLOSED\n\n"
                    )

                    message += (
                        f"Strategy: "
                        f"{ACTIVE_STRATEGY}\n"
                    )

                    message += (
                        f"Pair: {pair}\n"
                    )

                    message += (
                        f"Side: {side}\n"
                    )

                    message += (
                        f"PnL: "
                        f"${round(pnl_dollars, 2)}\n"
                    )

                    message += (
                        f"Balance: "
                        f"${round(balances[pair], 2)}\n"
                    )

                    message += "\n📊 ADVANCED METRICS\n"

                    message += (
                        f"Win Rate: "
                        f"{advanced['win_rate']}%\n"
                    )

                    message += (
                        f"Average Win: "
                        f"${advanced['avg_win']}\n"
                    )

                    message += (
                        f"Average Loss: "
                        f"${advanced['avg_loss']}\n"
                    )

                    message += (
                        f"Profit Factor: "
                        f"{advanced['profit_factor']}\n"
                    )

                    message += (
                        f"Max Drawdown: "
                        f"${advanced['max_drawdown']}\n"
                    )

                    message += (
                        f"Max Consecutive Losses: "
                        f"{advanced['max_consecutive_losses']}\n"
                    )

                    message += (
                        f"Largest Win: "
                        f"${advanced['largest_win']}\n"
                    )

                    message += (
                        f"Largest Loss: "
                        f"${advanced['largest_loss']}\n"
                    )

                    send_telegram(message)

                    positions[pair] = None

        except Exception as e:

            print(
                f"ERROR WITH {pair}: {e}"
            )

    print("Cycle complete. Sleeping...")

    time.sleep(SLEEP)
