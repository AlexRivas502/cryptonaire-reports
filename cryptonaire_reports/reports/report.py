import abc
from typing import List

import structlog
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.exchange_mappings import EXCHANGE_MAP


logger = structlog.get_logger()


class Report:

    def __init__(self, exchanges: List[str] = ["all"]) -> None:
        self.exchanges: List[Exchange] = []
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
                                "exchange_api_keys.config file. Add the following line "
                                "to be able to retrieve the information: \n"
                                f"\t\t\t\t[{exchange_instance.name}]\n"
                                "\t\t\t\tAPI_KEY=<YOUR API KEY>\n"
                                "\t\t\t\tSECRET_KEY=<YOUR SECRET KEY>\n"
                            )
                        continue
        if not self.exchanges:
            logger.error(f"Unable to retrieve data from any exchange. Exiting.")
            exit(1)

    @abc.abstractmethod
    def report(self):
        return
