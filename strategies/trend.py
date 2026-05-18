import pandas as pd

def calculate_indicators(df):
    df = df.copy()

    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()

    return df


def check_signal(df):

    if df is None or len(df) < 25:
        return None

    df = df.dropna()

    if len(df) < 25:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if pd.isna(prev["ma5"]) or pd.isna(prev["ma20"]):
        return None

    # BUY
    if prev["ma5"] < prev["ma20"] and curr["ma5"] > curr["ma20"]:
        return "BUY"

    # SELL
    if prev["ma5"] > prev["ma20"] and curr["ma5"] < curr["ma20"]:
        return "SELL"

    return None


def get_signal(df):
    df = calculate_indicators(df)
    return check_signal(df)
