import requests
from typing import List, Tuple

import structlog
from cryptonaire_reports.networks.network import Network
from dexscreener import DexscreenerClient
from dexscreener.models import TokenPair

logger = structlog.get_logger()

API_URL = "https://api.mainnet-beta.solana.com"
PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


class Solana(Network):

    def __init__(self) -> None:
        super().__init__("SOLANA")

    @property
    def name(self) -> str:
        return "Solana"

    def get_solana_balances(
        self,
    ) -> Tuple[
        List[Tuple[str, str, float]], List[Tuple[str, str, float, float, float]]
    ]:
        logger.info(f"[{self.name.upper()}] Extracting balances from Solana")
        balances_only = {}  # Map of mint: balances
        mint_balances = []  # Actual balances for mints. Includes price and market cap
        sol_balances = []
        try:
            source_name = f"Solana"
            for address in self._addresses:
                logger.info(f"[{self.name.upper()}] Extracting balances from {address}")
                # SOL Balance
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [
                        f"{address}",
                        {"encoding": "jsonParsed"},
                    ],
                }
                response = requests.post(API_URL, json=payload).json()
                # Value is in lamports, which is one billionth of a SOL
                sol_balance = float(response["result"]["value"]) * 0.000000001
                if symbol not in self.token_ignore_list:
                    sol_balances.append((source_name, "SOL", sol_balance, 0, 0))

                # Tokens Balance
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        f"{address}",
                        {"programId": f"{PROGRAM_ID}"},
                        {"encoding": "jsonParsed"},
                    ],
                }

                response = requests.post(API_URL, json=payload).json()
                logger.debug(f"[{self.name.upper()}] Full response: {response}")
                # Extract tokens balance
                for token in response["result"]["value"]:
                    token_info = token["account"]["data"]["parsed"]["info"]
                    mint = token_info["mint"]
                    exploded_balance = int(token_info["tokenAmount"]["amount"])
                    decimal_position = token_info["tokenAmount"]["decimals"]
                    divider = float("1e+" + str(decimal_position))
                    balance = exploded_balance / divider
                    if balance > 0:
                        balances_only[mint] = balance
                logger.debug(f"[{self.name.upper()}] Balances found: {balances_only}")

                # Use Dex Screener to extract symbol and market information
                logger.info(
                    f"[{self.name.upper()}] Extracting mint's symbols from {address}"
                )
                dex_client = DexscreenerClient()
                # There's a limit of 30 addresses per call
                curr_mint_list = []
                dex_mint_lists = []
                for mint in balances_only.keys():
                    curr_mint_list.append(mint)
                    if len(curr_mint_list) == 30:
                        dex_mint_lists.append(curr_mint_list)
                        curr_mint_list = []
                if len(curr_mint_list) > 0:  # Append the last one if it's not empty
                    dex_mint_lists.append(curr_mint_list)
                dex_responses = []
                for mint_list in dex_mint_lists:  # Operates in batches of 30
                    concat_mints = ",".join(mint_list)
                    logger.debug(f"Call to DEX: {concat_mints}")
                    dex_response = dex_client.get_token_pairs(address=concat_mints)
                    dex_responses.append(dex_response[0])

                token_pair: TokenPair
                for token_pair in dex_responses:
                    symbol = token_pair.base_token.symbol
                    balance = balances_only[token_pair.base_token.address]
                    # We have access to market information in the same call
                    price_usd = token_pair.price_usd
                    market_cap = token_pair.fdv

                    if symbol not in self.token_ignore_list:
                        mint_balances.append(
                            (source_name, symbol, balance, price_usd, market_cap)
                        )

            logger.debug(
                f"[{self.name.upper()}] Solana mint balances: \n{str(mint_balances)}"
            )
            logger.debug(
                f"[{self.name.upper()}] Solana SOL balances: \n{str(sol_balances)}"
            )
            return sol_balances, mint_balances
        except Exception as e:
            logger.error(
                f"[{self.name.upper()}] Error while retrieving balances from {self.name}"
            )
            logger.debug(f"[{self.name.upper()}] Full exception: {e}")
            return [], []

    def get_balances(
        self,
    ) -> Tuple[
        List[Tuple[str, str, float]], List[Tuple[str, str, float, float, float]]
    ]:
        balances = []
        sol_balances, mint_balances = self.get_solana_balances()
        balances.extend(sol_balances)
        balances.extend(mint_balances)
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
