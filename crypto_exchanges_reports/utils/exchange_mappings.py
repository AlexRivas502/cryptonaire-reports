from crypto_exchanges_reports.exchanges.binance import Binance
from crypto_exchanges_reports.exchanges.bing_x import BingX
from crypto_exchanges_reports.exchanges.bybit import ByBit
from crypto_exchanges_reports.exchanges.gate import Gate

EXCHANGE_MAP = {
    Binance: ["binance"],
    BingX: ["bing-x", "bingx", "bing_x"],
    ByBit: ["bybit", "by-bit"],
    Gate: ["gate", "gate-io", "gate_io"],
}
