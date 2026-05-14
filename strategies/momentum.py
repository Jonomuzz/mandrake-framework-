
def calculate_indicators(df):
    df["returns"] = df["close"].pct_change()

    df["momentum"] = df["returns"].rolling(window=5).sum()
    df["volume_ma"] = df["volume"].astype(float).rolling(window=10).mean()

    return df



def check_signal(df):
    if len(df) < 20:
        return None

    curr = df.iloc[-1]

    volume_spike = float(curr["volume"]) > (curr["volume_ma"] * 1.5)

    # BUY MOMENTUM
    if (
        curr["momentum"] > 0.01 and
        volume_spike
    ):
        return "BUY"

    # SELL WEAKNESS
    if curr["momentum"] < -0.005:
        return "SELL"

    return None
