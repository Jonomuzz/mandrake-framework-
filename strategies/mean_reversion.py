import numpy as np


# ----------------------------
# INDICATORS
# ----------------------------
def calculate_indicators(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["std20"] = df["close"].rolling(window=20).std()

    # Z-score = (price - mean) / std
    df["zscore"] = (df["close"] - df["ma20"]) / df["std20"]

    return df


# ----------------------------
# SIGNAL LOGIC (Z-SCORE BASED)
# ----------------------------
def check_signal(df):
    if len(df) < 25:
        return None

    curr = df.iloc[-1]

    z = curr["zscore"]

    # Safety check (avoid NaN / divide errors)
    if np.isnan(z):
        return None

    # ----------------------------
    # BUY: extremely oversold
    # ----------------------------
    if z < -2.0:
        return "BUY"

    # ----------------------------
    # SELL: extremely overbought
    # ----------------------------
    if z > 2.0:
        return "SELL"

    return None
