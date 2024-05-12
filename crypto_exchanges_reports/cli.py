import click

from crypto_exchanges_reports.reports.portfolio import Portfolio
from crypto_exchanges_reports.utils.logger import LoggerConfig
from crypto_exchanges_reports.utils.functions import parse_exchanges


@click.group()
def crypto_report():
    pass


@click.command()
@click.option(
    "--exchange",
    "-e",
    type=str,
    default="all",
    help="""Exchange to extract the information from. Defaults to all, which 
    generates a report with the information from all available exchanges (Binance,
    BingX and ByBit)""",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="""Exchange to extract the information from. Defaults to all, which 
    generates a report with the information from all available exchanges (Binance,
    BingX and ByBit)""",
)
def portfolio(exchange: str, debug: bool):
    LoggerConfig(log_level="debug" if debug else "info")
    exchanges = parse_exchanges(exchange)
    portfolio = Portfolio(exchanges=exchanges)
    portfolio.report()


crypto_report.add_command(portfolio)

if __name__ == "__main__":
    crypto_report()
