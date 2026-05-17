def calculate_indicators(df):
    df["high20"] = df["high"].rolling(20).max()
    df["low20"] = df["low"].rolling(20).min()
    return df


def check_signal(df):
    close = df["close"].iloc[-1]

    if close > df["high20"].iloc[-2]:
        return "BUY"

    if close < df["low20"].iloc[-2]:
        return "SELL"

    return None


def get_signal(df):
    df = calculate_indicators(df)
    return check_signal(df)
