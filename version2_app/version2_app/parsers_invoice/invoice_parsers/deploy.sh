#####  Invoice Parsers update Time and Date    ########
#git config --global alias.when '!stat -c %y .git/FETCH_HEAD'

### To update parsers swift to invoice_parses repo

cd /home/frappe/frappe-bench/apps/version2_app/version2_app/parsers_invoice/invoice_parsers

git config --global alias.when '!stat -c %y .git/FETCH_HEAD'
git when
git pull

