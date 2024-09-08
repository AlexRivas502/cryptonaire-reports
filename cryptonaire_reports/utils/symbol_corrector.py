SYMBOL_MAP = {"BEAMX": "BEAM", "RNDR": "RENDER", "ATOR": "ANYONE"}


def symbol_corrector(symbol: str) -> str:
    return SYMBOL_MAP[symbol] if symbol in SYMBOL_MAP else symbol
