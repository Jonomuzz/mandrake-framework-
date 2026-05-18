positions = {}


def has_position(symbol):
    return symbol in positions


def open_position(symbol, side, entry_price, size):
    positions[symbol] = {
        "side": side,
        "entry": entry_price,
        "size": size
    }



def close_position(symbol):
    if symbol in positions:
        del positions[symbol]



def get_position(symbol):
    return positions.get(symbol)
