@ECHO OFF
py -m pip install -i https://test.pypi.org/simple/  --extra-index-url https://pypi.org/simple cryptonaire-reports==0.1.0a1
curl -o exchange_api_keys_TEST.config https://raw.githubusercontent.com/AlexRivas502/cryptonaire-reports/main/templates/exchange_api_keys_test_template.config
