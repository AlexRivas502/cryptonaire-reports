from cryptonaire_reports.exchanges.binance import Binance
from cryptonaire_reports.exchanges.bing_x import BingX
from cryptonaire_reports.exchanges.bybit import ByBit
from cryptonaire_reports.exchanges.gate import Gate
from cryptonaire_reports.networks.ethereum import Ethereum
from cryptonaire_reports.networks.solana import Solana

EXCHANGE_MAP = {
    Binance: ["binance"],
    BingX: ["bing-x", "bingx", "bing_x"],
    ByBit: ["bybit", "by-bit"],
    Gate: ["gate", "gate-io", "gate_io"],
}

NETWORKS_MAP = {
    Ethereum: ["ethereum", "eth"],
    Solana: ["sol", "solana"],
}
