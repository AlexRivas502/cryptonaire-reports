import os
from typing import List, Tuple

import structlog
import pandas as pd

logger = structlog.get_logger()


def num_to_excel_col(num: int):
    if num < 1:
        raise ValueError("num must be >= 1")
    result = ""
    while num:
        num, rem = divmod(num - 1, 26)
        result = chr(ord("A") + rem) + result
    return result


def add_market_cap_classification(pdf_row, risk_levels: List[Tuple[str, int, int]]):
    for classification, lower_bound, upper_bound in risk_levels:
        lower_bound = 0 if not lower_bound else lower_bound
        upper_bound = float("inf") if not upper_bound else upper_bound
        if pdf_row["market_cap"] >= lower_bound and pdf_row["market_cap"] < upper_bound:
            return classification

    return "Unknown"
