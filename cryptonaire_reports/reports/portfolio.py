from typing import List, Dict, Set
from datetime import datetime
from pathlib import Path

import structlog
import pandas as pd
from cryptonaire_reports.reports.report import Report
from cryptonaire_reports.utils.coin_market_cap import CoinMarketCap

pd.options.display.float_format = "{:.2f}".format

logger = structlog.get_logger()


class Portfolio(Report):

    def __init__(self, exchanges: List[str] = ["all"]) -> None:
        super().__init__(exchanges)
        self.coin_market_cap = CoinMarketCap()

    def get_balances_from_exchanges(self) -> pd.DataFrame:
        """Gets the balances from all the configured exchanges.
        If you've got one coin across different exchanges, there will be one row per
        exchange. If you've got one coin across different wallets within an exchange
        (for example, having SOL in Spot and Earn), they will be two separate rows.

        Returns:
            pd.DataFrame: Pandas dataframe with the following columns:
                exchange, symbol, balance
        """
        balances = []
        for exchange in self.exchanges:
            exchange_balance = exchange.get_balances()
            if not exchange_balance:
                logger.debug(
                    f"[{exchange.name.upper()}] Balance data not found. Skipping."
                )
                continue
            logger.info(
                f"[{exchange.name.upper()}] Data collection completed successfully"
            )
            balances.extend([(exchange.name, *balance) for balance in exchange_balance])
        balances_pdf = pd.DataFrame(
            balances,
            columns=["exchange", "symbol", "balance"],
        )
        return balances_pdf

    def extract_additional_coin_info(self, symbols: Set[str]) -> Dict[str, Dict]:
        """Given a list of symbols, uses the CoinMarketCap API to extract additional
        information from the token. For each token, these columns are added:
        - name
        - price_usd
        - rank
        - market_cap
        - max_supply
        - total_supply
        - circulating_supply

        Args:
            symbols (Set[str]): Set of all the tokens that we want to enrich.
            detailed (bool): If True, adds additional data (see description), otherwise
                it just returns the full name and last price. Defaults to False.

        Returns:
            Dict[str, Dict]: Dictionary where the keys are the symbols and the values
                are dictionaries with all the columns mentioned before.
        """
        return self.coin_market_cap.get_coin_info(coin_list=symbols)

    @staticmethod
    def combine_balances(row: pd.DataFrame) -> pd.Series:
        result = {}
        result["exchanges"] = "|".join(set(row["exchange"]))
        result["balance"] = row["balance"].sum()
        return pd.Series(
            result,
            index=["exchanges", "balance"],
        )

    @staticmethod
    def get_rename_map() -> Dict[str, str]:
        return {
            "exchanges": "Exchange(s) / Network(s)",
            "symbol": "Symbol",
            "name": "Full Name",
            "rank": "Coin Rank",
            "market_cap": "Market Cap",
            "max_supply": "Max Supply",
            "total_supply": "Total Supply",
            "circulating_supply": "Circulating Supply",
            "balance": "Balance",
            "price_usd": "Price (USD)",
            "total_value_usd": "Total Value (USD)",
            "portfolio_percentage": "Portfolio Percentage",
        }

    def report(self):
        # Extract all the balances from the exchanges and networks
        exchange_balances_pdf = self.get_balances_from_exchanges()
        balances_pdf = exchange_balances_pdf

        # Group by ticker symbol and sum the balances
        groupped_balances_pdf = balances_pdf.groupby(by=["symbol"]).apply(
            self.combine_balances
        )

        # Extract additional information, including latest price, from each coin
        symbols = set(groupped_balances_pdf.index.tolist())
        coin_info_dict = self.extract_additional_coin_info(symbols=symbols)
        coin_info_pdf = pd.DataFrame.from_dict(coin_info_dict, orient="index")
        coin_info_pdf.index.name = "symbol"

        # Join the balances with the additional info and calculate total value and percentage
        report_pdf = groupped_balances_pdf.join(coin_info_pdf)
        report_pdf["total_value_usd"] = report_pdf["balance"] * report_pdf["price_usd"]
        report_pdf["portfolio_percentage"] = report_pdf[["total_value_usd"]].apply(
            lambda x: x / x.sum()
        )

        # Rename columns to a more readable format
        report_pdf.reset_index(inplace=True)
        report_pdf = report_pdf.rename(columns=self.get_rename_map())

        # Write out the CSV file
        output_dir = Path("reports/portfolio")
        output_dir.mkdir(parents=True, exist_ok=True)

        curr_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"crypto_portfolio_report_{curr_date}.csv"

        logger.info(f"Writing report to {output_dir / output_file_name}...")
        report_pdf.to_csv(
            output_dir / output_file_name,
            index=False,
            float_format="{:f}".format,
            encoding="utf-8",
        )
        logger.info(f"Report generated successfully: {output_dir / output_file_name}")
