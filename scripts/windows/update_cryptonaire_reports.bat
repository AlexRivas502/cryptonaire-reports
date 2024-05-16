@ECHO OFF
py -m pip install --upgrade --force-reinstall -i https://test.pypi.org/simple/  --extra-index-url https://pypi.org/simple cryptonaire-reports
IF NOT EXIST cryptonaire_reports.config curl -o cryptonaire_reports.config https://raw.githubusercontent.com/AlexRivas502/cryptonaire-reports/main/templates/cryptonaire_reports_template.config