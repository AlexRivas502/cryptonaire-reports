import time
from configparser import ConfigParser
from requests import Response
from typing import List, Dict, Set

import structlog
from coinmarketcapapi import CoinMarketCapAPI
from coinmarketcapapi import CoinMarketCapAPIError
from cryptonaire_reports.utils.singleton import Singleton

logger = structlog.get_logger()


class CoinMarketCap(metaclass=Singleton):

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("api_keys.config")
        if "CoinMarketCap" not in config:
            logger.error(f"CoinMarketCap configuration missing in api_keys.config")
            exit(1)
        self.api = CoinMarketCapAPI(api_key=config.get("CoinMarketCap", "API_KEY"))

    def get_coin_info(self, coin_list: Set[str]) -> List[Dict]:
        """Given a list of coins / ticker symbols, extracts additional information
        using the CoinMarketCap API.

        Args:
            coin_list (Set[str]): List of all the coins we want to extract info from.

        Returns:
            List[Dict]: Dictionary where the keys are the ticker symbols and the value
                is a dictionary with all the requested information
        """
        logger.info(
            f"[CoinMarketCap] Extracting basic info for: {', '.join(coin_list)}"
        )
        coin_market_cap_map_response: Response = self.api.cryptocurrency_map(
            symbol=",".join(coin_list)
        )
        # Results can contain duplicates. We only want to keep the first instance of
        # each symbol
        coin_info = {}
        for coin_map in coin_market_cap_map_response.data:
            if coin_map["symbol"].upper() in coin_info:
                continue
            coin_info[coin_map["symbol"].upper()] = {
                "id": coin_map.get("id"),
                "name": coin_map.get("name"),
                "rank": int(coin_map.get("rank") or -1),
            }
        not_found = set([coin.upper() for coin in coin_list]) - set(coin_info.keys())
        if not_found:
            logger.warning(
                f"[CoinMarketCap] The following symbols were not found: {','.join(not_found)}"
            )
        else:
            logger.info(
                f"[CoinMarketCap] Basic information found for: {', '.join(coin_list)}"
            )

        for symbol, info in coin_info.items():
            logger.info(f"[CoinMarketCap] Extracting latest price of {symbol}...")
            try:
                latest_quote = self.api.cryptocurrency_quotes_latest(
                    id=info["id"]
                ).data.get(str(info["id"]))
            except CoinMarketCapAPIError:
                logger.warning(
                    f"[CoinMarketCap] API limit reached. Waiting 60 seconds to reset..."
                )
                time.sleep(61)
                latest_quote = self.api.cryptocurrency_quotes_latest(
                    id=info["id"]
                ).data.get(str(info["id"]))

            if not latest_quote:
                logger.warning(f"[CoinMarketCap] Price data not found for: {symbol}")

            coin_info[symbol]["price_usd"] = float(
                latest_quote.get("quote").get("USD").get("price")
            )
            coin_info[symbol]["max_supply"] = int(latest_quote.get("max_supply") or -1)
            coin_info[symbol]["circulating_supply"] = int(
                latest_quote.get("circulating_supply") or -1
            )
            coin_info[symbol]["total_supply"] = int(
                latest_quote.get("total_supply") or -1
            )
            coin_info[symbol]["market_cap"] = int(
                latest_quote.get("quote").get("USD").get("market_cap") or -1
            )
        logger.debug(f"[CoinMarketCap] Additional Info Extracted: {coin_info}")
        return coin_info
