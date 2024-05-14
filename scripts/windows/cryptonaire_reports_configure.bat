@ECHO OFF
py -m pip install -i https://test.pypi.org/simple/  --extra-index-url https://pypi.org/simple cryptonaire-reports==0.1.0a2
curl -o api_keys.config https://raw.githubusercontent.com/AlexRivas502/cryptonaire-reports/main/templates/api_keys_template.config
