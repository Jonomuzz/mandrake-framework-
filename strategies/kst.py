import pandas as pd


def roc(series, period):
    return ((series - series.shift(period)) / series.shift(period)) * 100


def calculate_indicators(df):

    # =========================
    # 200 EMA TREND FILTER
    # =========================
    df["ema200"] = df["close"].ewm(span=200).mean()

    # =========================
    # KST COMPONENTS
    # =========================
    rcma1 = roc(df["close"], 10).rolling(10).mean()
    rcma2 = roc(df["close"], 15).rolling(15).mean()
    rcma3 = roc(df["close"], 20).rolling(20).mean()
    rcma4 = roc(df["close"], 30).rolling(30).mean()

    # =========================
    # KST LINE
    # =========================
    df["kst"] = (
        rcma1 * 1 +
        rcma2 * 2 +
        rcma3 * 3 +
        rcma4 * 4
    )

    # =========================
    # SIGNAL LINE
    # =========================
    df["signal"] = df["kst"].rolling(20).mean()

    return df


def check_signal(df):

    if len(df) < 250:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    # =========================
    # BUY CONDITIONS
    # =========================
    bullish_trend = curr["close"] > curr["ema200"]

    bullish_cross = (
        prev["kst"] < prev["signal"] and
        curr["kst"] > curr["signal"]
    )

    if bullish_trend and bullish_cross:
        return "BUY"

    # =========================
    # SELL CONDITIONS
    # =========================
    bearish_trend = curr["close"] < curr["ema200"]

    bearish_cross = (
        prev["kst"] > prev["signal"] and
        curr["kst"] < curr["signal"]
    )

    if bearish_trend and bearish_cross:
        return "SELL"

    return None
