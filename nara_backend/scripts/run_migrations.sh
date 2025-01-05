#!/bin/sh

# copying env file
ENV_FILE_DIR=$(dirname "$BASH_SOURCE")/../
if [[ ! -e ${ENV_FILE_DIR}/.env ]]; then
    cp ${ENV_FILE_DIR}/.env.sample ${ENV_FILE_DIR}/.env
fi

# Ensure database directory exists with proper permissions
echo "Setting up database directory"
DB_DIR="/app/nara_backend"
DB_FILE="$DB_DIR/db.sqlite3"

# Create parent directory if it doesn't exist
mkdir -p "$DB_DIR"

# Create empty database file if it doesn't exist
if [ ! -f "$DB_FILE" ]; then
    touch "$DB_FILE"
fi

# Set proper permissions
chown www-data:www-data "$DB_FILE"
chmod 666 "$DB_FILE"

echo "Running Database Migrations"
python manage.py makemigrations
python manage.py migrate

exec "$@"
