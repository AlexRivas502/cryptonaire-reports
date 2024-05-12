from typing import List
from datetime import datetime
from pathlib import Path

import structlog
import pandas as pd
from crypto_exchanges_portfolio_reports.exchanges.binance import Binance
from crypto_exchanges_portfolio_reports.exchanges.bing_x import BingX
from crypto_exchanges_portfolio_reports.exchanges.bybit import ByBit
from crypto_exchanges_portfolio_reports.exchanges.gate_io import GateIO
from crypto_exchanges_portfolio_reports.exchanges.exchange import Exchange
from crypto_exchanges_portfolio_reports.reports.report import Report

pd.options.display.float_format = "{:.10f}".format

logger = structlog.get_logger()


class Portfolio(Report):

    def __init__(self, exchanges: List[str] = ["all"]) -> None:
        super().__init__()
        self.exchanges: List[Exchange] = []
        logger.info(
            f"Looking for API keys of the following exchanges: {','.join(exchanges)}"
        )
        if "all" in exchanges:
            self.exchanges.append(Binance())
            self.exchanges.append(BingX())
            self.exchanges.append(ByBit())
            self.exchanges.append(GateIO())
        elif "binance" in exchanges:
            self.exchanges.append(Binance())
        elif "bing-x" in exchanges or "bingx" in exchanges or "bing_x" in exchanges:
            self.exchanges.append(BingX())
        elif "bybit" in exchanges or "by-bit" in exchanges:
            self.exchanges.append(ByBit())
        elif "gate-io" in exchanges or "gateio" in exchanges or "gate_io" in exchanges:
            self.exchanges.append(GateIO())

    def report(self):
        balances = []
        for exchange in self.exchanges:
            exchange_balance = exchange.get_balances()
            if not exchange_balance:
                logger.debug(f"Balance data not found for {exchange.name}. Skipping.")
                continue
            logger.info(f"Balance data found for {exchange.name}")
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
                index=["Exchange(s)", "Balance", "Current Price", "Total Value (USDT)"],
            )

        logger.info(f"Groupping assets by coin...")
        balances_pdf = (
            balances_pdf.groupby(by=["Ticker Symbol"])
            .apply(combine_balances)
            .reset_index()
        )
        # Remove duplicate exchanges
        # balances_pdf["Exchange(s)"]=balances_pdf["Exchange(s)"].str.split("|").map(set).str.join("|")
        balances_pdf = balances_pdf[
            [
                "Exchange(s)",
                "Ticker Symbol",
                "Balance",
                "Current Price",
                "Total Value (USDT)",
            ]
        ]
        logger.info(f"Writing report...")

        output_dir = Path("reports/portfolio")
        output_dir.mkdir(parents=True, exist_ok=True)

        curr_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"crypto_portfolio_report_{curr_date}.csv"

        balances_pdf.to_csv(output_dir / output_file_name, index=False)
        logger.info(f"Report generated successfully: {output_dir / output_file_name}")
