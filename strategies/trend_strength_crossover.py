def calculate_indicators(df):
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()

    # trend strength (direction + acceleration proxy)
    df["ma20_slope"] = df["ma20"].diff()

    # volatility filter (helps avoid chop)
    df["volatility"] = df["close"].pct_change().rolling(20).std()

    return df


def check_signal(df):
    ma5 = df["ma5"].iloc[-1]
    ma20 = df["ma20"].iloc[-1]
    slope = df["ma20_slope"].iloc[-1]
    vol = df["volatility"].iloc[-1]

    if pd.isna(ma5) or pd.isna(ma20) or pd.isna(slope):
        return None

    # trend strength filter (key edge)
    if abs(slope) < vol * 0.5:
        return None

    if ma5 > ma20 and slope > 0:
        return "BUY"

    if ma5 < ma20 and slope < 0:
        return "SELL"

    return None


def get_signal(df):
    return check_signal(calculate_indicators(df))
