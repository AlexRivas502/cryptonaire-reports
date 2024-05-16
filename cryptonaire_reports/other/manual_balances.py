import csv
from configparser import ConfigParser
from typing import Tuple, List

import structlog
import pandas as pd

logger = structlog.get_logger()


class ManualBalances:

    def __init__(self) -> None:
        config = ConfigParser()
        config.read("cryptonaire_reports.config")
        if "Manual Balances" not in config:
            logger.warning(
                f"Manual balance configuration not found. If you want to add manual "
                f"balances, you need to add the following section to your config "
                f"file: \n"
                f"\t\t\t\t[Manual Balances]\n"
                f"\t\t\t\tCSV_FILE= <local csv file path>\n"
                f"Your CSV file should contain three columns: source, symbol, balance"
            )
            self.active = False
            return

        if config.get("Manual Balances", "CSV_FILE"):
            self.csv_file_path = config.get("Manual Balances", "CSV_FILE")
        else:
            logger.warning(
                f"CSV_FILE configuration not found. Make sure to add the CSV_FILE "
                f"config to your Manual Balances section: \n"
                f"\t\t\t\t[Manual Balances]\n"
                f"\t\t\t\tCSV_FILE= <local csv file path>\n"
                f"Your CSV file should contain three columns: source, symbol, balance"
            )
            self.active = False

    @property
    def name(self) -> str:
        return "Manual"

    def get_balances(self) -> List[Tuple[str, float]]:
        balances_pdf = pd.read_csv(self.csv_file_path)
        balances = list(balances_pdf.itertuples(index=False, name=None))
        logger.info(f"[{self.name.upper()}] All balances extracted successfully")
        return balances
