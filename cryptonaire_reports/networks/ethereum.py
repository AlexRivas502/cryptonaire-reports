import requests
from typing import List, Tuple

import structlog
from cryptonaire_reports.networks.network import Network

logger = structlog.get_logger()

API_URL = "https://api.ethplorer.io"


class Ethereum(Network):

    def __init__(self) -> None:
        super().__init__("ETHEREUM")

    @property
    def name(self) -> str:
        return "Ethereum"

    def get_eth_mainnet_balances(self) -> List[Tuple[str, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from Ethereum Mainnet..."
        )
        mainnet_balances = []
        for address in self._addresses:
            address_info = requests.get(
                f"{API_URL}/getAddressInfo/{address}?apiKey=freekey"
            ).json()
            # Extract ETH Balance
            eth_balance = address_info["ETH"]["balance"]
            mainnet_balances.append(("ETH", eth_balance))
            # Extract additional tokens balance
            for token in address_info["tokens"]:
                symbol = token["tokenInfo"]["symbol"]
                exploded_balance = int(token["balance"])
                decimal_position = token["tokenInfo"]["decimals"]
                divider = float("1e+" + decimal_position)
                balance = exploded_balance / divider
                mainnet_balances.append((symbol, balance))
        logger.debug(
            f"[{self.name.upper()}] Ethereum Mainnet balances: \n{mainnet_balances}"
        )
        return mainnet_balances

    def get_balances(self) -> List[Tuple[str, float]]:
        balances = []
        balances.extend(self.get_eth_mainnet_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
