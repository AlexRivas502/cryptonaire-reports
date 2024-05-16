from typing import Tuple, List

import structlog
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector
from gate_api import ApiClient, Configuration
from gate_api.api.spot_api import SpotApi
from gate_api.models.spot_account import SpotAccount

logger = structlog.get_logger()

API_URL = "https://api.gateio.ws/api/v4"


class Gate(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("Gate")
        if not self.active:
            return
        config = Configuration(key=self._api_key, secret=self._secret_key, host=API_URL)
        self.spot_api = SpotApi(api_client=ApiClient(config))

    @property
    def name(self) -> str:
        return "Gate"

    def get_spot_balances(self) -> List[Tuple[str, float]]:
        """Extracts the balance from the spot account on Gate.io

        Returns:
            List[Tuple[str, float]]: List of tuples that cointain (symbol, balance)
        """
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        spot_balances = []
        coin_asset: SpotAccount
        for coin_asset in self.spot_api.list_spot_accounts():
            coin_ticker = symbol_corrector(coin_asset.currency)
            balance = float(coin_asset.available) + float(coin_asset.locked)
            if not balance > 0:
                continue
            spot_balances.append((coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
        return spot_balances

    def get_balances(self) -> List[Tuple[str, float]]:
        """Extracts the balances from the following accounts in gate.io:
        - Spot

        Returns:
            List[Tuple[str, float]]: List of tuples that cointain (symbol, balance)
        """
        balances = []
        balances.extend(self.get_spot_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
