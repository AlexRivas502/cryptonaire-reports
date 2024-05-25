import structlog

from typing import Tuple, List
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector
from pybit.unified_trading import HTTP

logger = structlog.get_logger()


class ByBit(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("ByBit")
        if not self.active:
            return
        self.client = HTTP(
            testnet=False, api_key=self._api_key, api_secret=self._secret_key
        )

    @property
    def name(self) -> str:
        return "ByBit"

    def get_unified_trading_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "ByBit (Unified Trading)"
        spot_balances = []
        unified_account_wallet = self.client.get_wallet_balance(accountType="UNIFIED")
        for coin_asset in unified_account_wallet["result"]["list"][0]["coin"]:
            coin_ticker = symbol_corrector(coin_asset["coin"])
            balance = float(coin_asset["equity"])
            if not balance > 0:
                continue
            spot_balances.append((source_name, coin_ticker, balance))
        logger.debug(
            f"[{self.name.upper()}] Unified trading balances: \n{spot_balances}"
        )
        return spot_balances

    def get_balances(self) -> List[Tuple[str, str, float]]:
        balances = []
        balances.extend(self.get_unified_trading_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
