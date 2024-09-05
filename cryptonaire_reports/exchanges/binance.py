import structlog

from typing import Tuple, List
from binance.spot import Spot
from binance.api import API
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector

logger = structlog.get_logger()


class Binance(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("Binance")
        if not self.active:
            return
        self.spot_client = Spot(self._api_key, self._secret_key)
        self.api = API(
            api_key=self._api_key,
            api_secret=self._secret_key,
            base_url="https://api.binance.com",
        )

    @property
    def name(self) -> str:
        return "Binance"

    def get_spot_balances(self) -> List[Tuple[str, str, float, float, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "Binance (Spot)"
        spot_balances = []
        try:
            response = self.spot_client.account(
                recvWindow=30000, omitZeroBalances="true"
            )
            logger.debug(f"[{self.name.upper()}] Full response: {response}")
            for coin_asset in response["balances"]:
                coin_ticker = symbol_corrector(coin_asset["asset"])
                if coin_ticker.startswith("LD") and len(coin_ticker) > 4:
                    # This value corresponds to a coin that's stored in Earn - Flexible
                    logger.debug(
                        f"[{self.name.upper()}] Found coin {coin_ticker}, skipping. "
                        f"Full info: {coin_asset}"
                    )
                    continue
                balance = float(coin_asset["free"]) + float(coin_asset["locked"])
                if not balance > 0:
                    continue
                # Last two elements are backup price and backup market cap
                spot_balances.append((source_name, coin_ticker, balance, 0, 0))
            logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
            return spot_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving spot balances from Binance"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_earn_flexible_balances(self) -> List[Tuple[str, str, float, float, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from flexible earn account..."
        )
        source_name = "Binance (Flexible Earn)"
        earn_balances = []
        try:
            all_products = []
            retrieved_all = False
            while not retrieved_all:
                response = self.spot_client.get_flexible_product_position(
                    recvWindow=30000, size=100
                )
                all_products.extend(response["rows"])
                total_expected = response["total"]
                if total_expected == len(all_products):
                    retrieved_all = True
                    logger.info(
                        f"[{self.name.upper()}] Retrieved {total_expected} products "
                        f"from flexible earn"
                    )
            logger.debug(f"[{self.name.upper()}] Full response: {all_products}")
            for product in response["rows"]:
                coin_ticker = symbol_corrector(product["asset"])
                balance = float(product["totalAmount"])
                if not balance > 0:
                    continue
                # Last two elements are backup price and backup market cap
                earn_balances.append((source_name, coin_ticker, balance, 0, 0))
            logger.debug(
                f"[{self.name.upper()}] Flexible Earn balances: \n{earn_balances}"
            )
            return earn_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving flexible balances from Binance"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_earn_locked_balances(self) -> List[Tuple[str, str, float, float, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from locked earn account..."
        )
        source_name = "Binance (Locked Earn)"
        earn_balances = []
        try:
            all_products = []
            retrieved_all = False
            while not retrieved_all:
                response = self.spot_client.get_locked_product_position(
                    recvWindow=30000, size=100
                )
                all_products.extend(response["rows"])
                total_expected = response["total"]
                if total_expected == len(all_products):
                    retrieved_all = True
                    logger.info(
                        f"[{self.name.upper()}] Retrieved {total_expected} products "
                        f"from locked earn"
                    )
            logger.debug(f"[{self.name.upper()}] Full response: {all_products}")
            for product in all_products:
                coin_ticker = symbol_corrector(product["asset"])
                balance = float(product["amount"])
                if not balance > 0:
                    continue
                earn_balances.append((source_name, coin_ticker, balance, 0, 0))
            logger.debug(
                f"[{self.name.upper()}] Locked Earn balances: \n{earn_balances}"
            )
            return earn_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving locked balances from Binance"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_balances(self) -> List[Tuple[str, str, float, float, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_earn_flexible_balances())
        balances.extend(self.get_earn_locked_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
