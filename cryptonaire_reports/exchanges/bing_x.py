import hmac
import json
import requests
import structlog
import time

from hashlib import sha256
from typing import Tuple, List, Dict, Optional
from cryptonaire_reports.exchanges.exchange import Exchange
from cryptonaire_reports.utils.singleton import Singleton
from cryptonaire_reports.utils.symbol_corrector import symbol_corrector

logger = structlog.get_logger()

API_URL = "https://open-api.bingx.com"


class BingX(Exchange, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__("BingX")
        if not self.active:
            return

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

    def get_spot_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Spot account...")
        source_name = "BingX (Spot)"
        spot_balances = []
        spot_acc_balance = self._api_request(
            endpoint="/openApi/spot/v1/account/balance"
        )
        for coin_asset in spot_acc_balance["data"]["balances"]:
            coin_ticker = symbol_corrector(coin_asset["asset"])
            balance = float(coin_asset["free"]) + float(coin_asset["locked"])
            if not balance > 0:
                continue
            spot_balances.append((source_name, coin_ticker, balance))
        logger.debug(f"[{self.name.upper()}] Spot balances: \n{spot_balances}")
        return spot_balances

    def get_wealth_balances(self) -> List[Tuple[str, str, float]]:
        logger.warning(
            f"[{self.name.upper()}] BingX doesn't provide wealth balances yet. That information "
            "must be entered manually until the API enables wealth balances."
        )
        return []

    def get_balances(self) -> List[Tuple[str, str, float]]:
        balances = []
        balances.extend(self.get_spot_balances())
        balances.extend(self.get_wealth_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
