import numpy as np
import pandas as pd


# =========================
# BASIC MOVING AVERAGES
# =========================
def add_moving_averages(df):
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma50"] = df["close"].rolling(window=50).mean() if len(df) >= 50 else df["ma20"]
    return df


# =========================
# Z SCORE (PRICE NORMALISATION)
# =========================
def add_zscore(df, window=20):

    mean = df["close"].rolling(window).mean()
    std = df["close"].rolling(window).std()

    df["zscore"] = (df["close"] - mean) / std.replace(0, np.nan)
    df["zscore"] = df["zscore"].fillna(0)

    return df


# =========================
# VOLUME INDICATORS
# =========================
def add_volume_indicators(df, window=20):

    if "volume" not in df.columns:
        df["volume"] = 0

    df["volume_ma"] = df["volume"].rolling(window).mean()
    df["volume_std"] = df["volume"].rolling(window).std()

    df["volume_ma"] = df["volume_ma"].fillna(df["volume"])
    df["volume_std"] = df["volume_std"].fillna(0)

    return df


# =========================
# VOLATILITY
# =========================
def add_volatility(df, window=20):

    df["volatility"] = df["close"].rolling(window).std()
    df["volatility"] = df["volatility"].fillna(0)

    return df


# =========================
# TREND FEATURES
# =========================
def add_trend_features(df):

    df["ma20_slope"] = df["ma20"].diff()
    df["ma5_slope"] = df["ma5"].diff()

    df["trend_strength"] = (
        df["ma20_slope"] / df["close"]
    ).replace([np.inf, -np.inf], 0).fillna(0)

    return df


# =========================
# MAIN PIPELINE
# =========================
def build_indicators(df):

    df = df.copy()

    df = add_moving_averages(df)
    df = add_zscore(df)
    df = add_volume_indicators(df)
    df = add_volatility(df)
    df = add_trend_features(df)

    return df
