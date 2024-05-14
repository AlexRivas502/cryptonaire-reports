from typing import Tuple, List

import structlog
from cryptonaire_reports.exchanges.exchange import Exchange
from gate_api import ApiClient, Configuration
from gate_api.api.spot_api import SpotApi
from gate_api.models.spot_account import SpotAccount
from gate_api.models.ticker import Ticker

logger = structlog.get_logger()

API_URL = "https://api.gateio.ws/api/v4"


class Gate(Exchange):

    def __init__(self) -> None:
        super().__init__("Gate")
        if not self.active:
            return
        config = Configuration(key=self._api_key, secret=self._secret_key, host=API_URL)
        self.spot_api = SpotApi(api_client=ApiClient(config))

    @property
    def name(self) -> str:
        return "Gate"

    def _get_price(self, coin_ticker: str, wallet_type: str) -> float:
        logger.debug(f"[GATE][{wallet_type}] Retrieving {coin_ticker} last price...")
        if coin_ticker in ["USDT", "USDC", "USD"]:
            return 1.0
        try:
            ticker: Ticker = self.spot_api.list_tickers(
                currency_pair=f"{coin_ticker}_USDT"
            )[0]
            curr_price_usdt = float(ticker.last)
        except:
            logger.warning(
                f"[GATE][{wallet_type}] {coin_ticker} average price not found. Using $0"
            )
            curr_price_usdt = 0.0
        return curr_price_usdt

    def get_spot_balances(self) -> List[Tuple[str, float, float, float]]:
        spot_balances = []
        coin_asset: SpotAccount
        for coin_asset in self.spot_api.list_spot_accounts():
            coin_ticker = coin_asset.currency
            balance = float(coin_asset.available) + float(coin_asset.locked)
            if not balance > 0:
                continue
            curr_price_usdt = self._get_price(
                coin_ticker=coin_ticker, wallet_type="SPOT"
            )
            total = balance * curr_price_usdt
            spot_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return spot_balances

    def get_balances(self) -> List[Tuple[str, float, float, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        return balances
