from collections import defaultdict

# =========================
# STATE TRACKING
# =========================
active_positions = {}

# Groups for crude correlation control
# (you can later replace with real correlation matrix)
symbol_groups = {
    "BTCUSDT": "crypto_large",
    "ETHUSDT": "crypto_large",
    "BNBUSDT": "crypto_large",

    "SOLUSDT": "crypto_mid",
    "XRPUSDT": "crypto_mid",
    "ADAUSDT": "crypto_mid",
    "DOGEUSDT": "crypto_mid",

    "AVAXUSDT": "crypto_mid",
    "LINKUSDT": "crypto_mid",
    "MATICUSDT": "crypto_mid",

    "LTCUSDT": "crypto_mid",
    "ATOMUSDT": "crypto_mid"
}

# Track open exposures per group
group_exposure = defaultdict(int)


# =========================
# REGISTER POSITION
# =========================
def register_position(symbol, strategy):
    group = symbol_groups.get(symbol, "unknown")
    active_positions[symbol] = strategy
    group_exposure[group] += 1


# =========================
# REMOVE POSITION
# =========================
def remove_position(symbol):
    group = symbol_groups.get(symbol, "unknown")

    if symbol in active_positions:
        del active_positions[symbol]
        group_exposure[group] = max(
            0,
            group_exposure[group] - 1
        )


# =========================
# CORRELATION BLOCK CHECK
# =========================
def is_correlated_block(symbol, strategy):

    group = symbol_groups.get(symbol, "unknown")

    # =========================
    # HARD LIMITS (simple but effective)
    # =========================
    if group == "crypto_large":
        # Only allow max 1 active large-cap position
        if group_exposure[group] >= 1:
            return True

    if group == "crypto_mid":
        # Allow max 3 mid-cap positions
        if group_exposure[group] >= 3:
            return True

    # =========================
    # STRATEGY DIVERSIFICATION RULE
    # =========================
    # Avoid stacking same strategy too heavily
    strategy_count = list(active_positions.values()).count(strategy)

    if strategy_count >= 4:
        return True

    return False
