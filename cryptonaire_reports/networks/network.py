import abc
from configparser import ConfigParser
from typing import Tuple

import structlog

logger = structlog.get_logger()


class Network:

    def __init__(self, network: str) -> None:
        config = ConfigParser()
        config.read("cryptonaire_reports.config")
        if "Networks" not in config:
            logger.warning(
                f"Network configuration not found. If you want to retrieve balances "
                f"from {network}, you need to add the following section to your config "
                f"file: \n"
                f"\t\t\t\t[Networks]\n"
                f"\t\t\t\t{network} = <Your address>\n"
                f"\t\t\t\t            <Your second address> ...\n"
            )
            self.active = False
            return

        if config.get("Networks", network):
            logger.info(f"Network addresses found for {network}")
            self.active = True
            addresses = config.get("Networks", network)
            self._addresses = addresses if isinstance(addresses, list) else [addresses]
        else:
            logger.warning(f"No addresses found for {network}, skipping network")
            self.active = False

    @property
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def get_balances(self) -> Tuple[str, float]:
        raise NotImplementedError
