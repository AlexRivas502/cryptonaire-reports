import structlog

from typing import Tuple, List
from cryptonaire_reports.exchanges.exchange import Exchange
from pybit.unified_trading import HTTP

logger = structlog.get_logger()


class ByBit(Exchange):

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

    def get_unified_trading_balances(self) -> List[Tuple[str, float, float, float]]:
        spot_balances = []
        unified_account_wallet = self.client.get_wallet_balance(accountType="UNIFIED")
        for coin_asset in unified_account_wallet["result"]["list"][0]["coin"]:
            coin_ticker = coin_asset["coin"]
            balance = float(coin_asset["equity"])
            if not balance > 0:
                continue
            total = float(coin_asset["usdValue"])
            logger.debug(
                f"[BYBIT][UNIFIED TRADING] Retrieving {coin_ticker} last price..."
            )
            curr_price_usdt = total / balance
            spot_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return spot_balances

    def get_balances(self) -> List[Tuple[str, float, float, float]]:
        balances = []
        balances.extend(self.get_unified_trading_balances())
        return balances
