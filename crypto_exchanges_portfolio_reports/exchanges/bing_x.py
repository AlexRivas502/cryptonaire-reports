import hmac
import json
import requests
import structlog
import time

from hashlib import sha256
from typing import Tuple, List, Dict, Optional
from crypto_exchanges_portfolio_reports.exchanges.exchange import Exchange

logger = structlog.get_logger()

API_URL = "https://open-api.bingx.com"


class BingX(Exchange):

    def __init__(self) -> None:
        super().__init__("BingX")

    @property
    def name(self) -> str:
        return "BingX"

    def _api_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        def _parse_param(params_map):
            sorted_keys = sorted(params_map)
            params_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sorted_keys])
            if params_str != "":
                return params_str + "&timestamp=" + str(int(time.time() * 1000))
            else:
                return params_str + "timestamp=" + str(int(time.time() * 1000))

        params = params or {}
        payload = {}
        method = "GET"
        params = _parse_param(params)
        signature = hmac.new(
            self._secret_key.encode("utf-8"), params.encode("utf-8"), digestmod=sha256
        ).hexdigest()
        url = "%s%s?%s&signature=%s" % (API_URL, endpoint, params, signature)
        headers = {"X-BX-APIKEY": self._api_key}
        response = requests.request(method, url, headers=headers, data=payload)
        return json.loads(response.text)

    def _get_price(self, coin_ticker: str, wallet_type: str) -> float:
        logger.debug(f"[BING-X][{wallet_type}] Retrieving {coin_ticker} last price...")
        if coin_ticker in ["USDT", "USDC", "USD"]:
            return 1.0
        try:
            curr_price_usdt = self._api_request(
                endpoint="/openApi/spot/v1/ticker/24hr",
                params={"symbol": f"{coin_ticker}-USDT"},
            )["data"][0]["lastPrice"]
        except:
            logger.warning(
                f"[BING-X][{wallet_type}] {coin_ticker} average price not found. Using $0"
            )
            curr_price_usdt = 0.0
        return curr_price_usdt

    def get_spot_balances(self) -> List[Tuple[str, float, float, float]]:
        spot_balances = []
        spot_acc_balance = self._api_request(
            endpoint="/openApi/spot/v1/account/balance"
        )
        for coin_asset in spot_acc_balance["data"]["balances"]:
            coin_ticker = coin_asset["asset"]
            balance = float(coin_asset["free"]) + float(coin_asset["locked"])
            if not balance > 0:
                continue
            curr_price_usdt = self._get_price(
                coin_ticker=coin_ticker, wallet_type="SPOT"
            )
            total = balance * curr_price_usdt
            spot_balances.append((coin_ticker, balance, curr_price_usdt, total))
        return spot_balances

    def get_wealth_balances(self) -> List[Tuple[str, float, float]]:
        logger.warning(
            "[BING-X][WEALTH] BingX doesn't provide wealth balances. That information "
            "must be entered manually until the API enables wealth balances."
        )
        return []

    def get_balances(self) -> List[Tuple[str, float, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_wealth_balances())
        return balances
