from typing import Set

import structlog

logger = structlog.get_logger()

SUPPORTED_EXCHANGES = {
    "Binance": ["binance"],
    "BingX": ["bing-x", "bingx", "bing_x"],
    "ByBit": ["bybit", "by-bit"],
    "GateIO": ["gate-io", "gateio", "gate_io"],
}


def parse_exchanges(exchanges_input: str) -> Set[str]:
    exchange_set: Set = {x.lower() for x in exchanges_input.split(",")}
    flat_list = ["all"]
    [flat_list.extend(x) for x in SUPPORTED_EXCHANGES.values()]
    supported_exchanges_codes = set(flat_list)
    if not exchange_set <= supported_exchanges_codes:
        not_supported = []
        for exchange in exchange_set:
            if exchange not in supported_exchanges_codes:
                not_supported.append(exchange)
        logger.error(
            f"The following exchange codes are not supported: {','.join(not_supported)}.\n"
            f"\t\t\t\tCurrently supported exchanges are {', '.join(SUPPORTED_EXCHANGES)}.\n"
            f"\t\t\t\tPlease use one of the following: {', '.join(flat_list)}."
        )
        exit(1)

    return exchange_set
