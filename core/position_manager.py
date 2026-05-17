positions = {}


def init(symbols):
    for s in symbols:
        positions[s] = None


def open_position(symbol):
    positions[symbol] = "LONG"


def close_position(symbol):
    positions[symbol] = None


def is_open(symbol):
    return positions[symbol] is not None
