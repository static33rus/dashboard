������� backup ����:
mysqldump --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root -p
������� restore ����:
mysql -u root -p < full-backup.sql