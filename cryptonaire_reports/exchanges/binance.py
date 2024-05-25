import structlog

from typing import Tuple, List
from binance.spot import Spot
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector

logger = structlog.get_logger()


class Binance(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("Binance")
        if not self.active:
            return
        self.client = Spot(self._api_key, self._secret_key)

    @property
    def name(self) -> str:
        return "Binance"

    def get_spot_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "Binance (Spot)"
        spot_balances = []
        for coin_asset in self.client.account(recvWindow=30000)["balances"]:
            coin_ticker = symbol_corrector(coin_asset["asset"])
            if coin_ticker.startswith("LD") and len(coin_ticker) > 4:
                # This value corresponds to a coin that's stored in Earn - Flexible
                continue
            balance = float(coin_asset["free"]) + float(coin_asset["locked"])
            if not balance > 0:
                continue
            spot_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
        return spot_balances

    def get_earn_flexible_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from Flexible Earn account..."
        )
        source_name = "Binance (Flexible Earn)"
        earn_balances = []
        for product in self.client.get_flexible_product_position(recvWindow=30000)[
            "rows"
        ]:
            coin_ticker = symbol_corrector(product["asset"])
            balance = float(product["totalAmount"])
            if not balance > 0:
                continue
            earn_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Flexible Earn balances: \n{earn_balances}")
        return earn_balances

    def get_earn_locked_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from Locked Earn account..."
        )
        source_name = "Binance (Locked Earn)"
        earn_balances = []
        for product in self.client.get_locked_product_position(recvWindow=30000)[
            "rows"
        ]:
            coin_ticker = symbol_corrector(product["asset"])
            balance = float(product["amount"])
            if not balance > 0:
                continue
            earn_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Locked Earn balances: \n{earn_balances}")
        return earn_balances

    def get_balances(self) -> List[Tuple[str, str, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_earn_flexible_balances())
        balances.extend(self.get_earn_locked_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
