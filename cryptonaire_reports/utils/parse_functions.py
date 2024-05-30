from typing import Set

import structlog
from cryptonaire_reports.utils.mappings import EXCHANGE_MAP, NETWORKS_MAP

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
            f"\t\t\t\tCurrently supported exchanges are {', '.join(EXCHANGE_MAP)}.\n"
            f"\t\t\t\tPlease use one of the following: {', '.join(flat_list)}."
        )
        exit(1)

    return exchange_set


def parse_networks(networks_input: str) -> Set[str]:
    network_set: Set = {x.lower() for x in networks_input.split(",")}
    flat_list = ["all"]
    [flat_list.extend(x) for x in NETWORKS_MAP.values()]
    supported_networks = set(flat_list)
    if not network_set <= supported_networks:
        not_supported = []
        for network in network_set:
            if network not in supported_networks:
                not_supported.append(network)
        logger.error(
            f"The following networks are not supported: {','.join(not_supported)}.\n"
            f"\t\t\t\tCurrently supported networks are {', '.join(NETWORKS_MAP)}.\n"
            f"\t\t\t\tPlease use one of the following: {', '.join(flat_list)}."
        )
        exit(1)

    return network_set
