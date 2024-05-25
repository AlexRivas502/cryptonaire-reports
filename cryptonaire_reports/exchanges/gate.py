from typing import Tuple, List

import structlog
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector
from gate_api import ApiClient, Configuration
from gate_api.api.spot_api import SpotApi
from gate_api.api.earn_uni_api import EarnUniApi
from gate_api.models.spot_account import SpotAccount
from gate_api.models.uni_lend import UniLend

logger = structlog.get_logger()

API_URL = "https://api.gateio.ws/api/v4"


class Gate(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("Gate")
        if not self.active:
            return
        config = Configuration(key=self._api_key, secret=self._secret_key, host=API_URL)
        self._api_client = ApiClient(config)
        self.spot_api = SpotApi(api_client=self._api_client)
        self.earn_uni_api = EarnUniApi(api_client=self._api_client)

    @property
    def name(self) -> str:
        return "Gate"

    def get_spot_balances(self) -> List[Tuple[str, str, float]]:
        """Extracts the balance from the spot account on Gate.io

        Returns:
            List[Tuple[str, float]]: List of tuples that cointain (symbol, balance)
        """
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "Gate (Spot)"
        spot_balances = []
        coin_asset: SpotAccount
        for coin_asset in self.spot_api.list_spot_accounts():
            coin_ticker = symbol_corrector(coin_asset.currency)
            balance = float(coin_asset.available) + float(coin_asset.locked)
            if not balance > 0:
                continue
            spot_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
        return spot_balances

    def get_earn_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Earn account...")
        source_name = "Gate (Earn)"
        earn_balances = []
        earn_lend: UniLend
        for earn_lend in self.earn_uni_api.list_user_uni_lends():
            coin_ticker = symbol_corrector(earn_lend.currency)
            balance = float(earn_lend.amount)
            if not balance > 0:
                continue
            earn_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Earn balances: \n{earn_balances}")
        return earn_balances

    def get_balances(self) -> List[Tuple[str, str, float]]:
        """Extracts the balances from the following accounts in gate.io:
        - Spot

        Returns:
            List[Tuple[str, float]]: List of tuples that cointain (symbol, balance)
        """
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_earn_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
