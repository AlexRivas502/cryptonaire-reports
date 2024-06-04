import abc
from typing import List

import structlog
from cryptonaire_reports.other.manual_balances import ManualBalances
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.networks.network import Network
from cryptonaire_reports.utils.mappings import EXCHANGE_MAP
from cryptonaire_reports.utils.mappings import NETWORKS_MAP


logger = structlog.get_logger()


class Report:

    def __init__(
        self,
        exchanges: List[str] = ["all"],
        networks: List[str] = ["all"],
        include_manual: bool = False,
    ) -> None:
        self.exchanges: List[Exchange] = []
        self.networks: List[Network] = []
        self.manual: ManualBalances = None
        if exchanges:
            self.initialize_exchanges(exchanges)
        if networks:
            self.initialize_networks(networks)
        if include_manual:
            self.manual = ManualBalances()

    def initialize_exchanges(self, exchanges: List[str]) -> None:
        logger.info(
            f"Looking for API keys of the following exchanges: {','.join(exchanges)}"
        )
        if "all" in exchanges:
            for exchange_class in EXCHANGE_MAP:
                exchange_instance = exchange_class()
                if exchange_instance.active:
                    self.exchanges.append(exchange_instance)
        else:
            for exchange in exchanges:
                for exchange_class, exchange_keys in EXCHANGE_MAP.items():
                    if exchange in exchange_keys:
                        exchange_instance = exchange_class()
                        if exchange_instance.active:
                            self.exchanges.append(exchange_instance)
                        else:
                            logger.warning(
                                f"Exchange {exchange} API keys were not found in "
                                "cryptonaire_reports.config file. Add the following line "
                                "to be able to retrieve the information: \n"
                                f"\t\t\t\t[{exchange_instance.name}]\n"
                                "\t\t\t\tAPI_KEY=<YOUR API KEY>\n"
                                "\t\t\t\tSECRET_KEY=<YOUR SECRET KEY>\n"
                            )
                        continue
        if not self.exchanges:
            logger.warning(f"Unable to retrieve data from any exchange. Exiting.")

    def initialize_networks(self, networks: List[str]) -> None:
        logger.info(
            f"Looking for addresses of the following networks: {','.join(networks)}"
        )
        if "all" in networks:
            for network_class in NETWORKS_MAP:
                network_instance = network_class()
                if network_instance.active:
                    self.networks.append(network_instance)
        else:
            for network in networks:
                for network_class, network_keys in NETWORKS_MAP.items():
                    if network in network_keys:
                        network_instance = network_class()
                        if network_instance.active:
                            self.networks.append(network_instance)
                        else:
                            logger.warning(
                                f"Network {network} was not found in "
                                "cryptonaire_reports.config file. Add the following line "
                                "to be able to retrieve the information: \n"
                                f"\t\t\t\t[Networks]\n"
                                "\t\t\t\t{{network_instance.name}} = <Address 1>\n"
                                "\t\t\t\t                            <Address 2>\n"
                            )
                        continue
        if not self.networks:
            logger.warning(f"Unable to retrieve data from any network.")

    @abc.abstractmethod
    def report(self):
        return
