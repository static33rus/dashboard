Сделать backup базы:
mysqldump --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root -p
Сделать restore базы:
mysql -u root -p < full-backup.sql