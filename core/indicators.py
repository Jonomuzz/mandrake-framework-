import pandas as pd


def build_indicators(df):

    # =========================
    # MOVING AVERAGES
    # =========================
    df["ma5"] = (
        df["close"]
        .rolling(5)
        .mean()
    )

    df["ma20"] = (
        df["close"]
        .rolling(20)
        .mean()
    )

    df["ma50"] = (
        df["close"]
        .rolling(50)
        .mean()
    )

    # =========================
    # TREND
    # =========================
    df["trend_strength"] = (
        df["ma20"].diff()
    )

    # =========================
    # VOLATILITY
    # =========================
    df["volatility"] = (
        df["close"]
        .rolling(20)
        .std()
    )

    # =========================
    # Z SCORE
    # =========================
    rolling_std = (
        df["close"]
        .rolling(20)
        .std()
    )

    df["zscore"] = (
        (df["close"] - df["ma20"])
        / rolling_std
    )

    # =========================
    # VOLUME
    # =========================
    df["volume_ma"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    # =========================
    # CANDLE RANGE
    # =========================
    df["range"] = (
        df["high"] - df["low"]
    )

    # =========================
    # ATR STYLE RANGE
    # =========================
    df["range_ma"] = (
        df["range"]
        .rolling(14)
        .mean()
    )

    # =========================
    # MOMENTUM
    # =========================
    df["momentum"] = (
        df["close"] - df["close"].shift(5)
    )

    return df
