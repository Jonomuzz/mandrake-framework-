positions = {}


def has_position(symbol):
    return symbol in positions


def open_position(symbol, side, price, strategy):

    positions[symbol] = {
        "side": side,
        "entry_price": price,
        "strategy": strategy
    }


def close_position(symbol):

    if symbol in positions:
        del positions[symbol]


def get_position(symbol):
    return positions.get(symbol)
