# Cryptonaire Reports
Generates reports based on your crypto assets across different exchanges and wallets (Currently supports Binance, BingX, GateIO and ByBit)

## Installation
1. Clone the project
2. Make sure that you are using at least Python 3.11. Then run
   ```bash
   pip install cryptonaire-reports
   ```
3. You can access the command by running `crypto-report <REPORT TYPE>`. See third section for the supported reports.

## Seting up your API keys
Within the same folder you are running `crypto-report`, create a file called `exchange_api_keys.config` with the following structure:

```config
[Binance]
API_KEY = <your api key>
SECRET_KEY = <your secret key>

[BingX]
API_KEY = <your api key>
SECRET_KEY = <your secret key>

[ByBit]
API_KEY = <your api key>
SECRET_KEY = <your secret key>

[Gate]
API_KEY = <your api key>
SECRET_KEY = <your secret key>
```
Make sure to include all the API keys from the exchanges you want to read from. It is recommended that these API keys have read-only permissions

## Portfolio Report
You can get your total number of assets across all exchanges by running the following:
```bash
crypto-report portfolio --exchange <all|binance|bing_x|bybit|gate>
```

If you select `all`, it will generate a report based on all the exchanges you have configured
