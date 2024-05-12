from typing import Set

import structlog
from crypto_exchanges_reports.utils.exchange_mappings import EXCHANGE_MAP

logger = structlog.get_logger()


def parse_exchanges(exchanges_input: str) -> Set[str]:
    exchange_set: Set = {x.lower() for x in exchanges_input.split(",")}
    flat_list = ["all"]
    [flat_list.extend(x) for x in EXCHANGE_MAP.values()]
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
