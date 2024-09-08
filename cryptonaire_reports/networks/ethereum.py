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

    def get_eth_mainnet_balances(self) -> List[Tuple[str, str, float]]:
        logger.info(
            f"[{self.name.upper()}] Extracting balances from Ethereum Mainnet..."
        )
        mainnet_balances = []
        try:
            for address in self._addresses:
                source_name = f"Ethereum Wallet"
                address_info = requests.get(
                    f"{API_URL}/getAddressInfo/{address}?apiKey=freekey"
                ).json()
                # Extract ETH Balance
                eth_balance = address_info["ETH"]["balance"]
                mainnet_balances.append((source_name, "ETH", eth_balance, 0, 0))
                # Extract additional tokens balance
                for token in address_info["tokens"]:
                    symbol = token["tokenInfo"]["symbol"]
                    exploded_balance = int(token["balance"])
                    decimal_position = token["tokenInfo"]["decimals"]
                    divider = float("1e+" + decimal_position)
                    balance = exploded_balance / divider

                    if symbol not in self.token_ignore_list:
                        # Last two elements are backup price and backup market cap
                        mainnet_balances.append((source_name, symbol, balance, 0, 0))

            logger.debug(
                f"[{self.name.upper()}] Ethereum Mainnet balances: \n{mainnet_balances}"
            )
            return mainnet_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving balances from {self.name.upper()}"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return []

    def get_balances(self) -> List[Tuple[str, str, float, float, float]]:
        balances = []
        balances.extend(self.get_eth_mainnet_balances())
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
