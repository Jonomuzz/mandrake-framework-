import time
import os
import requests
import pandas as pd

from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)

# ================= CORE =================
from core.indicators import build_indicators
from core.trade_filter import (
    is_high_quality_setup,
    register_trade
)

from core.accounting import (
    log_trade,
    load_trades
)

from core.capital_allocator import (
    rebalance_capital,
    get_allocation,
    get_allocation_report
)

from core.correlation import (
    register_position,
    remove_position,
    is_correlated_block
)

from core.strategy_guard import (
    evaluate_strategies,
    is_disabled
)

from core.dashboard import generate_dashboard

# ================= CONFIG =================
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "MATICUSDT",
    "LTCUSDT",
    "ATOMUSDT"
]

INTERVAL = "1m"
LIMIT = 100
SLEEP = 60

START_BALANCE = 500

BASE_URL = "https://api.binance.com/api/v3/klines"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")

# ================= STATE =================
positions = {}
entry_price = {}
entry_strategy = {}
position_size = {}
entry_time = {}

last_dashboard = time.time()

# ================= TELEGRAM =================
def send_telegram(message):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# ================= DATA =================
def get_klines(symbol):

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    df = pd.DataFrame(data)

    df["open"] = df[1].astype(float)
    df["high"] = df[2].astype(float)
    df["low"] = df[3].astype(float)
    df["close"] = df[4].astype(float)
    df["volume"] = df[5].astype(float)

    return df

# ================= REGIME ENGINE =================
def select_strategy(df):

    curr = df.iloc[-1]

    volatility = curr.get("volatility", 0)
    trend_strength = abs(curr.get("trend_strength", 0))
    zscore = abs(curr.get("zscore", 0))

    # =========================
    # STRONG TREND
    # =========================
    if trend_strength > 0.0015:
        return "trend"

    # =========================
    # BREAKOUT
    # =========================
    if volatility > df["volatility"].mean() * 1.5:
        return "breakout"

    # =========================
    # MOMENTUM
    # =========================
    if trend_strength > 0.0008:
        return "momentum"

    # =========================
    # MEAN REVERSION
    # =========================
    if zscore > 1:
        return "mean_reversion"

    return "mean_reversion"

# ================= SIGNAL ROUTER =================
def get_signal(df, strategy):

    if strategy == "trend":
        return trend_strength_crossover.check_signal(df)

    if strategy == "mean_reversion":
        return mean_reversion.check_signal(df)

    if strategy == "breakout":
        return breakout.check_signal(df)

    if strategy == "momentum":
        return momentum.check_signal(df)

    if strategy == "kst":
        return kst.check_signal(df)

    return None

# ================= EXECUTION =================
def execute_trade(symbol, signal, price, strategy):

    global positions

    # =========================
    # BUY
    # =========================
    if signal == "BUY" and positions.get(symbol) is None:

        # Correlation protection
        if is_correlated_block(symbol, strategy):
            return

        allocation = get_allocation(strategy)

        size = START_BALANCE * allocation

        positions[symbol] = "LONG"
        entry_price[symbol] = price
        entry_strategy[symbol] = strategy
        position_size[symbol] = size
        entry_time[symbol] = time.time()

        register_position(symbol, strategy)
        register_trade(symbol)

        msg = (
            f"🟢 BUY {symbol}\n"
            f"Strategy: {strategy}\n"
            f"Price: {price}\n"
            f"Size: ${round(size, 2)}"
        )

        print(msg)
        send_telegram(msg)

    # =========================
    # SELL
    # =========================
    elif signal == "SELL" and positions.get(symbol) == "LONG":

        entry = entry_price[symbol]
        size = position_size[symbol]

        pnl_pct = ((price - entry) / entry) * 100
        pnl_usd = size * (pnl_pct / 100)

        strategy = entry_strategy[symbol]

        log_trade(
            symbol=symbol,
            strategy=strategy,
            side="LONG",
            entry_price=entry,
            exit_price=price,
            size=size,
            pnl=pnl_usd
        )

        remove_position(symbol)

        msg = (
            f"🔴 SELL {symbol}\n"
            f"Strategy: {strategy}\n"
            f"PnL: {round(pnl_pct, 2)}%\n"
            f"Profit: ${round(pnl_usd, 2)}"
        )

        print(msg)
        send_telegram(msg)

        positions[symbol] = None
        entry_price[symbol] = 0
        entry_strategy[symbol] = None
        position_size[symbol] = 0

# ================= MAIN LOOP =================
def run():

    global last_dashboard

    print("🚀 OVERTRADING FILTER ENGINE STARTED")

    send_telegram(
        "🚀 OVERTRADING FILTER ENGINE STARTED"
    )

    while True:

        try:

            # =========================
            # UPDATE CAPITAL ALLOCATION
            # =========================
            rebalance_capital()

            # =========================
            # CHECK STRATEGY HEALTH
            # =========================
            evaluate_strategies()

            # =========================
            # LOOP SYMBOLS
            # =========================
            for symbol in SYMBOLS:

                try:

                    df = get_klines(symbol)

                    # Build ALL indicators
                    df = build_indicators(df)

                    strategy = select_strategy(df)

                    # Skip disabled strategies
                    if is_disabled(strategy):
                        continue

                    signal = get_signal(df, strategy)

                    price = df.iloc[-1]["close"]

                    print(
                        f"{symbol} | "
                        f"{strategy} | "
                        f"{signal}"
                    )

                    # =========================
                    # QUALITY FILTER
                    # =========================
                    if signal:

                        high_quality = is_high_quality_setup(
                            df,
                            strategy,
                            symbol
                        )

                        if not high_quality:
                            continue

                        execute_trade(
                            symbol,
                            signal,
                            price,
                            strategy
                        )

                except Exception as e:
                    print(f"Error {symbol}: {e}")

            # =========================
            # DASHBOARD
            # =========================
            elapsed = time.time() - last_dashboard

            if elapsed > 1800:

                send_telegram(
                    generate_dashboard()
                )

                send_telegram(
                    get_allocation_report()
                )

                last_dashboard = time.time()

            print("Cycle complete...\n")

            time.sleep(SLEEP)

        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(30)

# ================= START =================
if __name__ == "__main__":
    run()
