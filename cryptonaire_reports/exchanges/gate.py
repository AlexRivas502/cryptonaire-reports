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

    def get_spot_balances(self) -> List[Tuple[str, str, float, float, float]]:
        """Extracts the balance from the spot account on Gate.io

        Returns:
            List[Tuple[str, float]]: List of tuples that cointain (symbol, balance)
        """
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "Gate (Spot)"
        spot_balances = []
        try:
            coin_asset: SpotAccount
            response = self.spot_api.list_spot_accounts()
            logger.debug(f"[{self.name.upper()}] Full response: {response}")
            for coin_asset in response:
                coin_ticker = symbol_corrector(coin_asset.currency)
                balance = float(coin_asset.available) + float(coin_asset.locked)
                if not balance > 0:
                    continue
                # Last two elements are backup price and backup market cap
                spot_balances.append((source_name, coin_ticker, balance, 0, 0))
            logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
            return spot_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving spot balances from {self.name.upper()}"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_earn_balances(self) -> List[Tuple[str, str, float, float, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Earn account...")
        source_name = "Gate (Earn)"
        earn_balances = []
        try:
            earn_lend: UniLend
            response = self.earn_uni_api.list_user_uni_lends()
            logger.debug(f"[{self.name.upper()}] Full response: {response}")
            for earn_lend in response:
                coin_ticker = symbol_corrector(earn_lend.currency)
                balance = float(earn_lend.amount)
                if not balance > 0:
                    continue
                # Last two elements are backup price and backup market cap
                earn_balances.append((source_name, coin_ticker, balance, 0, 0))
            logger.debug(f"[{self.name.upper()}] Earn balances: \n{earn_balances}")
            return earn_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving earn balances from {self.name.upper()}"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_balances(self) -> List[Tuple[str, str, float, float, float]]:
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
