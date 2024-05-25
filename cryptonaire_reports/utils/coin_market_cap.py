import time
from configparser import ConfigParser
from typing import List, Dict, Set

import structlog
from coinmarketcapapi import CoinMarketCapAPI
from coinmarketcapapi import CoinMarketCapAPIError
from coinmarketcapapi import Response
from cryptonaire_reports.utils.singleton import Singleton

logger = structlog.get_logger()


class CoinMarketCap(metaclass=Singleton):

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("cryptonaire_reports.config")
        if "CoinMarketCap" not in config:
            logger.error(
                f"CoinMarketCap configuration missing in cryptonaire_reports.config"
            )
            exit(1)
        try:
            self.api = CoinMarketCapAPI(api_key=config.get("CoinMarketCap", "API_KEY"))
        except:
            logger.error(
                f"[CoinMarketCap] Error while configuring the CoinMarketCap API. Double"
                f"check that the API key is valid."
            )
            exit(1)

    def extract_cryptocurrency_map_from_api(self, coin_list: Set[str]) -> List[Dict]:
        try:
            coin_market_cap_map_response: Response = self.api.cryptocurrency_map(
                symbol=",".join(coin_list)
            )
            logger.info(
                f"[CoinMarketCap] Cryptocurrency map information for "
                f"{','.join(coin_list)} successfully extracted from API"
            )
            logger.debug(
                f"[CoinMarketCap] Full repsonse: {coin_market_cap_map_response}"
            )
            return coin_market_cap_map_response.data
        except CoinMarketCapAPIError as e:
            error_response: Response = e.rep
            logger.debug(f"[CoinMarketCap] Full error: {error_response}")
            if error_response.error_code == 400:
                # Bad request, one or more coins were not found. Try one by one
                if len(coin_list) == 1:
                    # This particular coin was not found, return []
                    logger.error(
                        f"[CoinMarketCap] The coin {next(iter(coin_list))} was not "
                        f"found in CoinMarketCap. All the information will be missing."
                    )
                    return []
                else:
                    logger.warning(
                        f"[CoinMarketCap] Failed to fetch cryptocurrency map info for "
                        "all the coins in one API call. Trying making one call per coin"
                    )
                    batch_responses = []
                    for symbol in coin_list:
                        res = self.extract_cryptocurrency_map_from_api(
                            coin_list={symbol}
                        )
                        print(res)
                        batch_responses.extend(res)
                    return batch_responses

            elif error_response.error_code in [401, 403]:
                logger.error(
                    f"[CoinMarketCap] Failed to retrieve info from API. Access to the "
                    f"cryptocurrency map is forbidden or unauthorized"
                )
                exit(1)
            elif error_response.error_code in [429, 1008]:
                # Request limit reached
                logger.warning(
                    f"[CoinMarketCap] API limit reached. Waiting 60 seconds to resume..."
                )
                time.sleep(61)
                return self.extract_cryptocurrency_map_from_api(coin_list=coin_list)
            elif error_response.error_code == 500:
                # Internal server error
                logger.error(
                    f"[CoinMarketCap] There is a problem with the CoinMarketCap API. "
                    f"Please try again later"
                )
                exit(1)
            else:
                logger.error(
                    f"[CoinMarketCap] Unknown error happened. Please create an issue "
                    f"in the Github project to solve this problem. Include the "
                    f"following in your request: {error_response}"
                )
                exit(1)

    def get_coin_info(self, coin_list: Set[str]) -> List[Dict]:
        """Given a list of coins / ticker symbols, extracts additional information
        using the CoinMarketCap API.

        Args:
            coin_list (Set[str]): List of all the coins we want to extract info from.

        Returns:
            List[Dict]: Dictionary where the keys are the ticker symbols and the value
                is a dictionary with all the requested information
        """
        cryptocurrency_map = self.extract_cryptocurrency_map_from_api(coin_list)

        # Results can contain duplicates. We only want to keep the first instance of
        # each symbol
        coin_info = {}
        for coin_map in cryptocurrency_map:
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
                try:
                    latest_quote = self.api.cryptocurrency_quotes_latest(
                        id=info["id"]
                    ).data.get(str(info["id"]))
                except:
                    logger.error(f"[CoinMarketCap] Price data not found for: {symbol}")
                    latest_quote = None

            if not latest_quote:
                logger.warning(f"[CoinMarketCap] Price data not found for: {symbol}")
            else:
                coin_info[symbol]["price_usd"] = float(
                    latest_quote.get("quote").get("USD").get("price")
                )
                coin_info[symbol]["max_supply"] = int(
                    latest_quote.get("max_supply") or -1
                )
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
