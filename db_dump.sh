echo "Starting database dump..."
mysqldump -u jflynn87 -h jflynn87.mysql.pythonanywhere-services.com --set-gtid-purged=OFF --no-tablespaces --column-statistics=0 'jflynn87$orig_games' -p > db-backup.sql

echo "Database dump completed. Backup saved to db-backup.sql"