@ECHO OFF
py -m pip install -i https://test.pypi.org/simple/  --extra-index-url https://pypi.org/simple cryptonaire-reports
curl -o cryptonaire_reports_template.config https://raw.githubusercontent.com/AlexRivas502/cryptonaire-reports/main/templates/cryptonaire_reports_template.config
