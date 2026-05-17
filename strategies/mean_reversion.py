import pandas as pd


def calculate_indicators(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()

    df["zscore"] = (df["close"] - df["ma20"]) / df["std20"]
    return df


def check_signal(df):
    z = df["zscore"].iloc[-1]

    if z < -1.5:
        return "BUY"
    elif z > 1.5:
        return "SELL"

    return None


def get_signal(df):
    df = calculate_indicators(df)
    return check_signal(df)
