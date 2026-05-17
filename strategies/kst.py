def calculate_indicators(df):
    # Rate of change components
    r1 = df["close"].pct_change(10)
    r2 = df["close"].pct_change(15)
    r3 = df["close"].pct_change(20)
    r4 = df["close"].pct_change(30)

    # smoothed KST line
    df["kst"] = (
        r1.rolling(10).mean() * 1 +
        r2.rolling(10).mean() * 2 +
        r3.rolling(10).mean() * 3 +
        r4.rolling(15).mean() * 4
    )

    df["kst_signal"] = df["kst"].rolling(5).mean()

    return df


def check_signal(df):
    kst = df["kst"].iloc[-1]
    signal = df["kst_signal"].iloc[-1]

    if pd.isna(kst) or pd.isna(signal):
        return None

    # crossover logic
    prev_kst = df["kst"].iloc[-2]
    prev_signal = df["kst_signal"].iloc[-2]

    if prev_kst < prev_signal and kst > signal:
        return "BUY"

    if prev_kst > prev_signal and kst < signal:
        return "SELL"

    return None


def get_signal(df):
    return check_signal(calculate_indicators(df))
