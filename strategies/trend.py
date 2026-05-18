import pandas as pd


def calculate_indicators(df):
    """
    Fast trend strategy indicators
    """

    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()

    return df


def check_signal(df):
    """
    Fast MA crossover logic
    """

    if len(df) < 25:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    # BUY crossover
    if prev["ma5"] < prev["ma20"] and curr["ma5"] > curr["ma20"]:
        return "BUY"

    # SELL crossover
    if prev["ma5"] > prev["ma20"] and curr["ma5"] < curr["ma20"]:
        return "SELL"

    return None


def get_signal(df):

    df = calculate_indicators(df)

    signal = check_signal(df)

    return signal
