from typing import List, Dict, Set, Tuple
from datetime import datetime
from pathlib import Path

import structlog
import pandas as pd
from cryptonaire_reports.reports.report import Report
from cryptonaire_reports.utils.coin_market_cap import CoinMarketCap

pd.options.display.float_format = "{:.2f}".format

logger = structlog.get_logger()


class Portfolio(Report):

    def __init__(
        self,
        exchanges: List[str] = ["all"],
        networks: List[str] = ["all"],
        include_manual: bool = False,
        raw: bool = False
    ) -> None:
        super().__init__(exchanges, networks, include_manual)
        self.coin_market_cap = CoinMarketCap()
        self.raw_format = raw

    def get_balances_from_exchanges(self) -> List[Tuple[str, str, float, float, float]]:
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
            balances.extend(exchange_balance)
        return balances

    def get_balances_from_networks(self) -> List[Tuple[str, str, float, float, float]]:
        """Gets the balances from all the configured networks.
        If you've got one coin across different networks, there will be one row per
        network.

        Returns:
            pd.DataFrame: Pandas dataframe with the following columns:
                network, symbol, balance
        """
        balances = []
        for network in self.networks:
            network_balance = network.get_balances()
            if not network_balance:
                logger.debug(
                    f"[{network.name.upper()}] Balance data not found. Skipping."
                )
                continue
            logger.info(
                f"[{network.name.upper()}] Data collection completed successfully"
            )
            balances.extend(network_balance)
        return balances

    def get_balances_from_manual_file(
        self,
    ) -> List[Tuple[str, str, float, float, float]]:
        if not self.manual:
            return []
        balances = self.manual.get_balances()
        f"[{self.manual.name.upper()}] Data collection completed successfully"
        return balances

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
        result["source"] = "|".join(set(row["source"]))
        result["balance"] = row["balance"].sum()
        result["price_backup"] = row["price_backup"].max()
        result["market_cap_backup"] = row["market_cap_backup"].max()
        return pd.Series(
            result,
            index=["source", "balance", "price_backup", "market_cap_backup"],
        )

    @staticmethod
    def get_rename_map() -> Dict[str, str]:
        return {
            "source": "Exchange(s) / Network(s)",
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

    def write_csv_report(self, report_pdf: pd.DataFrame, path: Path) -> None:
        curr_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file_name = f"crypto_portfolio_report_{curr_date}.csv"

        logger.info(f"Writing report to {path / output_file_name}...")
        report_pdf.to_csv(
            path / output_file_name,
            index=False,
            float_format="{:f}".format,
            encoding="utf-8",
        )
        logger.info(f"Report generated successfully: {path / output_file_name}")

    def write_excel_report(self, report_pdf: pd.DataFrame, path: Path) -> None:
        logger.info(f"Generating XLSX report")
        curr_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"crypto_portfolio_report_{curr_date}.xlsx"

        # Remove all the tokens that have less than $1
        report_pdf = report_pdf[report_pdf["Total Value (USD)"] >= 1.00]
        excluded_tokens = report_pdf[report_pdf["Total Value (USD)"] < 1.00]["Symbol"].unique()
        logger.info(
            f"Excluding tokens {','.join(excluded_tokens)} from report since their "
            f"balance is less than $1.00"
        )

        ##### GENERATE XLSX FILE WITH XLSXWRITER #####
        # Skip the header to be able to create a custom header format instead of using
        # the pandas default one
        writer = pd.ExcelWriter(path=path / output_file_name, engine='xlsxwriter')
        report_pdf.sort_values(by=["Total Value (USD)"]).to_excel(
            writer, 
            sheet_name='Portfolio', 
            startrow=1, 
            index=False, 
            header=False
        )
        workbook  = writer.book
        worksheet = writer.sheets['Portfolio']
        total_rows = report_pdf.shape[0]
        total_cols = report_pdf.shape[1]

        # Format the data
        columns_format = {
            "Symbol": {"align": "center", "bold": "True"},
            "Exchange(s) / Network(s)": {},
            "Balance": {"num_format": "#,##0.00000000"},
            "id": {"align": "center"},
            "Full Name": {"align": "left"},
            "Coin Rank": {"num_format": "#,##0", "align": "center"},
            "Price (USD)": {"num_format": "$#,##0.0000"},
            "Max Supply": {"num_format": "#,##0"},
            "Circulating Supply": {"num_format": "#,##0"},
            "Total Supply": {"num_format": "#,##0"},
            "Market Cap": {"num_format": "$#,##0"},
            "Total Value (USD)": {"num_format": "$#,##0.00"},
            "Portfolio Percentage": {"num_format": "0.00%", "align": "center"},
        }
        global_format = {"font_name": "Avenir Next LT Pro"}
        header_format = workbook.add_format(
            {
                "font_name": "Avenir Next LT Pro",
                "align": "center",
                "bold": "True", 
                "border": 1,
                "font_color": "white",
                "fg_color": "#30353D",
            }
        )

        column_lengths = []
        for idx, column in enumerate(columns_format):
            series = report_pdf[column]
            format = workbook.add_format({**columns_format[column], **global_format})
            max_len = (
                max(
                    (
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name)),  # len of column name/header
                    )
                )
                + 7  # adding a little extra space
            )
            column_lengths.append(max_len)
            worksheet.set_column(idx, idx, max_len, format)

            # Write the header
            worksheet.write(0, idx, column, header_format)

        # Generate the pie chart
        chart = workbook.add_chart({"type": "pie"})

        # Configure the series
        chart.add_series(
            {
                "name": "Cryptocurrency Percentage",
                "categories": f"=Portfolio!$A$2:$A${total_rows + 1}",
                "values": f"=Portfolio!$L$2:$L${total_rows + 1}",
                "data_labels": {
                    "value": True,
                    "category": True,
                    "percentage": True,
                    "separator": '\n',
                    "num_format": "0.00%",
                    "position": "outside_end",
                    "font": {"name": "Avenir Next LT Pro"},
                },
            }
        )
        chart.set_style(18)
        chart.set_size({'width': 1080, 'height': 1080})

        # Add a title.
        total_usd = '${:0,.2f}'.format(report_pdf["Total Value (USD)"].sum())
        chart.set_title(
            {
                "name": f"Crypto Portfolio - {datetime.now().strftime("%Y/%m/%d")}\nTotal value: {total_usd}",
                "name_font": {
                    "name": "Avenir Next LT Pro",
                },
            }
        )

        # Turn off the chart border.
        chart.set_chartarea({'border': {'none': True}})

        # Turn off the chart legend.
        chart.set_legend({"none": True})

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart(
            f"B{total_rows + 3}", 
            chart, 
            {"x_offset": 0, "y_offset": 0}
        )

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()
        writer.handles = None

        logger.info(f"Report generated successfully: {path / output_file_name}")

    def report(self):
        # Extract all the balances from the exchanges and networks
        exchange_balances = self.get_balances_from_exchanges()
        network_balances = self.get_balances_from_networks()
        manual_balances = self.get_balances_from_manual_file()
        balances = exchange_balances + network_balances + manual_balances
        balances_pdf = pd.DataFrame(
            balances,
            columns=[
                "source",
                "symbol",
                "balance",
                "price_backup",
                "market_cap_backup",
            ],
        )
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
        # Some balances have price and market cap info
        report_pdf["price_usd"] = (
            report_pdf[["price_usd", "price_backup"]]
            .bfill(
                axis=1,
            )
            .iloc[:, 0]
        )
        report_pdf["market_cap"] = (
            report_pdf[["market_cap", "market_cap_backup"]].bfill(axis=1).iloc[:, 0]
        )
        report_pdf.drop(["price_backup", "market_cap_backup"], axis=1, inplace=True)
        # Calculate total value and percentage
        report_pdf["total_value_usd"] = report_pdf["balance"] * report_pdf["price_usd"]
        report_pdf["portfolio_percentage"] = report_pdf[["total_value_usd"]].apply(
            lambda x: x / x.sum()
        )

        # Rename columns to a more readable format
        report_pdf.reset_index(inplace=True)
        report_pdf = report_pdf.rename(columns=self.get_rename_map())

        # Write out Excel file (formatted) or CSV file (raw)
        output_dir = Path("reports/portfolio")
        output_dir.mkdir(parents=True, exist_ok=True)
        if self.raw_format:
            self.write_csv_report(report_pdf=report_pdf, path=output_dir)
        else:
            self.write_excel_report(report_pdf=report_pdf, path=output_dir)
