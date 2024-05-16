SYMBOL_MAP = {
    "BEAMX": "BEAM",
}


def symbol_corrector(symbol: str) -> str:
    symbol_corrections = {"BEAMX": "BEAM"}
    return SYMBOL_MAP[symbol] if symbol in SYMBOL_MAP else symbol
