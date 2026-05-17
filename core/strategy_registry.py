from strategies import (
    mean_reversion,
    trend_strength_crossover,
    breakout,
    momentum,
    kst
)


def get_strategy(name):
    mapping = {
        "mean_reversion": mean_reversion,
        "trend": trend_strength_crossover,
        "breakout": breakout,
        "momentum": momentum,
        "kst": kst
    }
    return mapping.get(name)
