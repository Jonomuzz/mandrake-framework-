
def calculate_indicators(df):
    df["high_20"] = df["high"].astype(float).rolling(window=20).max()
    df["low_20"] = df["low"].astype(float).rolling(window=20).min()

    df["range"] = df["high_20"] - df["low_20"]
    df["avg_range"] = df["range"].rolling(window=10).mean()

    return df



def check_signal(df):
    if len(df) < 30:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    breakout_strength = curr["range"] > curr["avg_range"]

    # BUY BREAKOUT
    if (
        curr["close"] > prev["high_20"] and
        breakout_strength
    ):
        return "BUY"

    # SELL BREAKDOWN
    if curr["close"] < prev["low_20"]:
        return "SELL"

    return None
