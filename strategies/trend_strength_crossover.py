def calculate_indicators(df):
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma20_slope"] = df["ma20"].diff()

    return df


def check_signal(df):
    if df["ma5"].iloc[-1] > df["ma20"].iloc[-1] and df["ma20_slope"].iloc[-1] > 0:
        return "BUY"

    if df["ma5"].iloc[-1] < df["ma20"].iloc[-1] and df["ma20_slope"].iloc[-1] < 0:
        return "SELL"

    return None


def get_signal(df):
    df = calculate_indicators(df)
    return check_signal(df)
