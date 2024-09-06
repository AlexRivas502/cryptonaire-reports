import structlog

from typing import Tuple, List, Dict, Optional
from coinbase.rest import RESTClient
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector

logger = structlog.get_logger()


class Coinbase(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("Coinbase")
        if not self.active:
            return
        self.client = RESTClient(api_key=self._api_key, api_secret=self._secret_key)

    @property
    def name(self) -> str:
        return "Coinbase"

    def get_spot_balances(self) -> List[Tuple[str, str, float, float, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        spot_balances = []
        source_name = f"{self.name} (Spot)"

        try:
            accounts = self.client.get_accounts()
            logger.debug(f"[{self.name.upper()}] Full response: {accounts}")

            for account in accounts["accounts"]:
                available = account["available_balance"]
                hold = account["hold"]
                coin_ticker = symbol_corrector(available["currency"])
                balance = float(available["value"]) + float(hold["value"])
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

    def get_balances(self) -> List[Tuple[str, str, float, float, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
