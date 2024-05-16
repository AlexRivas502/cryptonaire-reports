import click

from cryptonaire_reports.reports.portfolio import Portfolio
from cryptonaire_reports.utils.parse_functions import parse_exchanges
from cryptonaire_reports.utils.parse_functions import parse_networks
from cryptonaire_reports.utils.logger import LoggerConfig


@click.group()
def crypto_report():
    pass


@click.command()
@click.option(
    "--networks",
    "-n",
    type=str,
    default=None,
    help="""Networks from which we want to extract balances from (Currently supports:
    Ethereum). Defaults to None. If set to all, it generates a report with all avaiable 
    networks in the config file""",
)
@click.option(
    "--exchanges",
    "-e",
    type=str,
    default=None,
    help="""Exchanges to extract the information from. Defaults to None. If set to all, 
    it generates a report with the information from all available exchanges (Binance,
    BingX, Gate and ByBit)""",
)
@click.option(
    "--include-manual",
    "-m",
    is_flag=True,
    default=False,
    help="""Includes the balances of a CSV file located in CSV_PATH.""",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="""Exchange to extract the information from. Defaults to all, which 
    generates a report with the information from all available exchanges (Binance,
    BingX, Gate and ByBit)""",
)
def portfolio(networks: str, exchanges: str, include_manual: bool, debug: bool):
    LoggerConfig(log_level="debug" if debug else "info")
    exchanges = parse_exchanges(exchanges) if exchanges else []
    networks = parse_networks(networks) if networks else []
    portfolio = Portfolio(
        exchanges=exchanges, networks=networks, include_manual=include_manual
    )
    portfolio.report()


crypto_report.add_command(portfolio)

if __name__ == "__main__":
    crypto_report()
