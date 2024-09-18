#!/bin/sh

MIGRATION_FILE=$(dirname "$BASH_SOURCE")/run_migrations.sh
/bin/bash ${MIGRATION_FILE}
echo "Running Server"
python manage.py runserver

exec "$@"
