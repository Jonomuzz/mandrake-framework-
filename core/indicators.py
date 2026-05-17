import pandas as pd


def build_indicators(df):

    # =========================
    # BASIC PRICES
    # =========================
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # =========================
    # MOVING AVERAGES
    # =========================
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()

    # =========================
    # MA DERIVATIVES
    # =========================
    df["ma20_slope"] = df["ma20"].diff()
    df["ma20_std"] = df["ma20"].rolling(20).std()

    # =========================
    # TREND + VOLATILITY
    # =========================
    df["trend_strength"] = df["ma20"].diff()
    df["volatility"] = df["close"].rolling(20).std()

    # =========================
    # Z SCORE
    # =========================
    rolling_std = df["close"].rolling(20).std()
    df["zscore"] = (df["close"] - df["ma20"]) / rolling_std

    # =========================
    # VOLUME FEATURES
    # =========================
    df["volume_ma"] = df["volume"].rolling(20).mean()

    # =========================
    # RANGE FEATURES
    # =========================
    df["range"] = df["high"] - df["low"]
    df["avg_range"] = df["range"].rolling(14).mean()

    # =========================
    # HIGH / LOW ROLLING FEATURES (FIX FOR YOUR ERROR)
    # =========================
    df["high_20"] = df["high"].rolling(20).max()
    df["low_20"] = df["low"].rolling(20).min()

    df["high_50"] = df["high"].rolling(50).max()
    df["low_50"] = df["low"].rolling(50).min()

    # =========================
    # MOMENTUM
    # =========================
    df["momentum"] = df["close"] - df["close"].shift(5)

    return df
