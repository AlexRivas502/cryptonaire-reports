from typing import List
from datetime import datetime
from pathlib import Path

import structlog
import pandas as pd
from cryptonaire_reports.reports.report import Report

pd.options.display.float_format = "{:.10f}".format

logger = structlog.get_logger()


class Portfolio(Report):

    def __init__(self, exchanges: List[str] = ["all"]) -> None:
        super().__init__(exchanges)

    def report(self):
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
            columns=[
                "Exchange",
                "Ticker Symbol",
                "Balance",
                "Current Price",
                "Total Value (USDT)",
            ],
        )

        def combine_balances(row: pd.DataFrame) -> pd.Series:
            result = {}
            result["Exchange(s)"] = "|".join(set(row["Exchange"]))
            result["Balance"] = row["Balance"].sum()
            result["Current Price"] = row["Current Price"].max()
            result["Total Value (USDT)"] = (
                row["Balance"].sum() * row["Current Price"].max()
            )
            return pd.Series(
                result,
                index=[
                    "Exchange(s)",
                    "Balance",
                    "Current Price",
                    "Total Value (USDT)",
                    "Percentage",
                ],
            )

        balances_pdf = balances_pdf.groupby(by=["Ticker Symbol"]).apply(
            combine_balances
        )
        balances_pdf["Portfolio Percentage"] = balances_pdf[
            ["Total Value (USDT)"]
        ].apply(lambda x: x / x.sum())
        balances_pdf.reset_index(inplace=True)
        balances_pdf = balances_pdf[
            [
                "Exchange(s)",
                "Ticker Symbol",
                "Balance",
                "Current Price",
                "Total Value (USDT)",
                "Portfolio Percentage",
            ]
        ]
        # balances_pdf["Total Value (USDT)"] = "XXXXX"
        # balances_pdf["Balance"] = "XXXXX"
        logger.info(f"Writing report...")

        output_dir = Path("reports/portfolio")
        output_dir.mkdir(parents=True, exist_ok=True)

        curr_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"crypto_portfolio_report_{curr_date}.csv"

        balances_pdf.to_csv(output_dir / output_file_name, index=False)
        logger.info(f"Report generated successfully: {output_dir / output_file_name}")
