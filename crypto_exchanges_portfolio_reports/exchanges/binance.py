import structlog

from typing import Tuple, List
from binance.spot import Spot
from crypto_exchanges_portfolio_reports.exchanges.exchange import Exchange

logger = structlog.get_logger()


class Binance(Exchange):

    def __init__(self) -> None:
        super().__init__("Binance")
        self.client = Spot(self._api_key, self._secret_key)

    @property
    def name(self) -> str:
        return "Binance"

    def _get_price(self, coin_ticker: str, wallet_type: str) -> float:
        logger.debug(f"[BINANCE][{wallet_type}] Retrieving {coin_ticker} last price...")
        if coin_ticker in ["USDT", "USDC", "USD"]:
            return 1.0
        try:
            curr_price_usdt = float(
                self.client.avg_price(f"{coin_ticker}USDT")["price"]
            )
        except:
            logger.warning(
                f"[BINANCE][{wallet_type}] {coin_ticker} average price not found. Using $0"
            )
            curr_price_usdt = 0.0
        return curr_price_usdt

    def get_spot_balances(self) -> List[Tuple[str, float, float, float]]:
        spot_balances = []
        for coin_asset in self.client.account()["balances"]:
            coin_ticker = coin_asset["asset"]
            if coin_ticker.startswith("LD") and len(coin_ticker) > 4:
                # This value corresponds to a coin that's stored in Earn - Flexible
                continue
            balance = float(coin_asset["free"]) + float(coin_asset["locked"])
            if not balance > 0:
                continue
            curr_price_usdt = self._get_price(
                coin_ticker=coin_ticker, wallet_type="SPOT"
            )
            total = balance * curr_price_usdt
            spot_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return spot_balances

    def get_earn_flexible_balances(self) -> List[Tuple[str, float, float, float]]:
        earn_balances = []
        for product in self.client.get_flexible_product_position()["rows"]:
            coin_ticker = product["asset"]
            balance = float(product["totalAmount"])
            if not balance > 0:
                continue
            curr_price_usdt = self._get_price(
                coin_ticker=coin_ticker, wallet_type="EARN - FLEXIBLE"
            )
            total = balance * curr_price_usdt
            earn_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return earn_balances

    def get_earn_locked_balances(self) -> List[Tuple[str, float, float, float]]:
        earn_balances = []
        for product in self.client.get_locked_product_position()["rows"]:
            coin_ticker = product["asset"]
            balance = float(product["amount"])
            if not balance > 0:
                continue
            curr_price_usdt = self._get_price(
                coin_ticker=coin_ticker, wallet_type="EARN - LOCKED"
            )
            total = balance * curr_price_usdt
            earn_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return earn_balances

    def get_balances(self) -> List[Tuple[str, float, float, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_earn_flexible_balances())
        balances.extend(self.get_earn_locked_balances())
        return balances
