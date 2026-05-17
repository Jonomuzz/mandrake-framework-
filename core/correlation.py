open_positions = {}

def register_position(symbol, strategy):
    open_positions[symbol] = strategy


def remove_position(symbol):
    open_positions.pop(symbol, None)


def is_correlated_block(symbol, strategy):
    """
    Prevent overexposure to same strategy across many assets
    """

    active = list(open_positions.values())

    same = active.count(strategy)

    # block if too many same-strategy positions
    if same >= 4:
        return True

    return False
