def calculate_indicators(df):
    """
    Fast trend strategy indicators (early signal detection)
    """
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()
    return df


def check_signal(df):
    """
    Fast MA crossover strategy (no slope filter, early entries)
    """
    if len(df) < 25:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    # BUY: fast crossover up
    if prev["ma5"] < prev["ma20"] and curr["ma5"] > curr["ma20"]:
        return "BUY"

    # SELL: fast crossover down
    if prev["ma5"] > prev["ma20"] and curr["ma5"] < curr["ma20"]:
        return "SELL"

    return None
