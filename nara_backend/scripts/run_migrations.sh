#!/bin/sh

# copying env file
ENV_FILE_DIR=$(dirname "$BASH_SOURCE")/../
if [[ ! -e ${ENV_FILE_DIR}/.env ]]; then
    cp ${ENV_FILE_DIR}/.env.sample ${ENV_FILE_DIR}/.env
fi

echo "Running Database Migrations"
python manage.py makemigrations
python manage.py migrate


exec "$@"
