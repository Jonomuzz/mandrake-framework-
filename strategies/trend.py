
def calculate_indicators(df):
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()

    df["ma20_slope"] = df["ma20"].diff()
    df["ma20_std"] = df["ma20"].rolling(window=20).std()

    return df



def check_signal(df):
    if len(df) < 25:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    slope_threshold = curr["ma20_std"] * 0.1

    distance = abs(curr["close"] - curr["ma20"]) / curr["ma20"]

    # BUY
    if (
        prev["ma5"] < prev["ma20"] and
        curr["ma5"] > curr["ma20"] and
        curr["ma20_slope"] > slope_threshold and
        distance > 0.001
    ):
        return "BUY"

    # SELL
    if (
        prev["ma5"] > prev["ma20"] and
        curr["ma5"] < curr["ma20"] and
        curr["ma20_slope"] < -slope_threshold and
        distance > 0.001
    ):
        return "SELL"

    return None
