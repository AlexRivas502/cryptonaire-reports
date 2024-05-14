import abc
from typing import Tuple
from configparser import ConfigParser

import structlog

logger = structlog.get_logger()


class Exchange:

    def __init__(self, exchange_name: str) -> None:
        config = ConfigParser()
        config.read("exchange_api_keys.config")
        if exchange_name not in config:
            logger.warning(f"No keys found for {exchange_name}, skipping exchange")
            self.active = False
        else:
            logger.info(f"API keys found for {exchange_name}")
            self.active = True
            self._api_key = config.get(exchange_name, "API_KEY")
            self._secret_key = config.get(exchange_name, "SECRET_KEY")

    @property
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def get_balances(self) -> Tuple[str, float]:
        raise NotImplementedError
