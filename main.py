import time

from core.config import PAIRS
from core.config import SLEEP
from core.config import ACTIVE_STRATEGY

from core.data import get_klines
from core.telegram import send_telegram
from core.execution import initialize_pairs
from core.execution import handle_trade
from core.metrics import send_metrics


# ================= STRATEGY LOADER =================
if ACTIVE_STRATEGY == "trend":
    from strategies.trend import calculate_indicators
    from strategies.trend import check_signal

else:
    raise Exception(f"Unknown strategy: {ACTIVE_STRATEGY}")


# ================= MAIN LOOP =================
def run_bot():
    print("Bot started...")

    send_telegram(
        f"🚀 Bot Started - Strategy: {ACTIVE_STRATEGY}"
    )

    initialize_pairs(PAIRS)

    last_metrics_time = time.time()

    while True:
        for pair in PAIRS:
            try:
                print(f"Checking {pair}...")

                df = get_klines(pair)

                df = calculate_indicators(df)

                signal = check_signal(df)

                price = df.iloc[-1]["close"]

                if signal:
                    handle_trade(pair, signal, price)

            except Exception as e:
                error_msg = f"⚠️ Error on {pair}: {str(e)}"

                print(error_msg)
                send_telegram(error_msg)

        if time.time() - last_metrics_time > 1800:
            send_metrics(PAIRS)
            last_metrics_time = time.time()

        print("Cycle complete. Sleeping...\n")

        time.sleep(SLEEP)


if __name__ == "__main__":
    print("FRAMEWORK BOT RUNNING")
    run_bot()
