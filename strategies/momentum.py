def calculate_indicators(df):
    df["ret"] = df["close"].pct_change()
    df["momentum"] = df["ret"].rolling(10).mean()
    return df


def check_signal(df):
    m = df["momentum"].iloc[-1]

    if m > 0.002:
        return "BUY"
    elif m < -0.002:
        return "SELL"

    return None


def get_signal(df):
    df = calculate_indicators(df)
    return check_signal(df)
