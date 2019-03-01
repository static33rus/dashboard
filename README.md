Запускаемые файлы:
--- dashboard.py - запускает дашборд

--- get_report.py - получить отчет в excel на почту:
запускается с параметрами [daily/weekly/big3] и [release/develop]
daily - это отчет по прогону ALL_OPERATOR_IMS
weekly - отчет по прогонам Beeline,MTS,Megafon,Sbertel,RTK
big3 - отчет по MTS,Beeline,Megafon
release/develop - это ветка mass'a
Отчет отправляется на почту, почта сейчас захардкожена. За отправку на почту отвечает функция sendmail

--- fill_database.py - скрипт, который записывает результаты функциональных тестов в базу данных. Запускается как post-build-action после прогонов Beeline,MTS,Megafon,Sbertel,RTK
запускается с параметрами [operator] [job] [dumptemplate] [build ]


Модули:
--- database.py - класс который нужен для подключения к базе и записи/чтения информации. Используется и dashbord.py и get_report.py
--- report.py - содержит два класса: первый создает excel файл с нужными данными, второй класс нужен для форматирования.
--- chart.py - небольшой класс, нужен для графиков в excele

СУБД:
user: dash
password: 12121212
mariadb на лонгхоле. Содержит 2 bd: autotest и autotest_perf
autotest - используется для функциональных тестов. 
autotest_perf - используется для dpdk performance тестов (точнее на момент моего ухода не используется, так как Женя сломал код)


Сделать backup базы:
mysqldump --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root -p
Сделать restore базы:
mysql -u root -p < full-backup.sql
Дебаг:
docker logs some-mariadb