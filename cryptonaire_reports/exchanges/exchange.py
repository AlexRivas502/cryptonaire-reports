import abc
from typing import Tuple, List
from configparser import ConfigParser

import structlog

logger = structlog.get_logger()


class Exchange:

    def __init__(self, exchange_name: str) -> None:
        config = ConfigParser()
        config.read("cryptonaire_reports.config")
        if exchange_name not in config:
            logger.warning(f"No keys found for {exchange_name}, skipping exchange")
            self.active = False
        else:
            logger.info(f"API keys found for {exchange_name}")
            self.active = True
            self._api_key = config.get(exchange_name, "API_KEY")
            self._secret_key = config.get(exchange_name, "SECRET_KEY")
            try:
                self.token_ignore_list = config.get(
                    "Ignore Tokens", exchange_name.upper()
                ).split(",")
                logger.info(
                    f"Token ignore list for {exchange_name}: "
                    f"{",".join(self.token_ignore_list)}"
                )
            except:
                self.token_ignore_list = []
                logger.debug(f"Token ignore list is empty for {exchange_name}")

    @property
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def get_balances(self) -> Tuple[str, str, float]:
        raise NotImplementedError
