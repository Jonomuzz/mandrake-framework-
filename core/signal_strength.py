def score_signal(df, signal_type):
    """
    Returns score from 0–100 based on indicator quality.
    """

    score = 50  # base score

    latest = df.iloc[-1]

    # Trend strength
    if "ma20_slope" in df:
        slope = latest.get("ma20_slope", 0)
        if abs(slope) > 0:
            score += min(20, abs(slope) * 1000)

    # Volatility boost
    if "ma20_std" in df:
        vol = latest.get("ma20_std", 0)
        if vol > 0:
            score += min(10, vol * 10)

    # Distance from MA (mean reversion quality)
    if "ma20" in df:
        distance = abs(latest["close"] - latest["ma20"]) / latest["ma20"]
        score += min(20, distance * 500)

    # Signal type weighting
    if signal_type == "trend":
        score += 5
    elif signal_type == "breakout":
        score += 10
    elif signal_type == "momentum":
        score += 8
    elif signal_type == "mean_reversion":
        score += 3

    return min(100, max(0, score))
