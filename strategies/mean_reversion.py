def calculate_indicators(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["std"] = df["close"].rolling(window=20).std()

    df["upper_band"] = df["ma20"] + (df["std"] * 2)
    df["lower_band"] = df["ma20"] - (df["std"] * 2)

    return df


def check_signal(df):
    if len(df) < 25:
        return None

    curr = df.iloc[-1]

    # BUY OVERSOLD
    if curr["close"] < curr["lower_band"]:
        return "BUY"

    # SELL OVERBOUGHT (FIXED INDENTATION)
    if curr["close"] > curr["upper_band"]:
        return "SELL"

    return None
