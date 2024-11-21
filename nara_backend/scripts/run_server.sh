#!/bin/sh

# Run migrations
MIGRATION_FILE="/app/nara_backend/scripts/run_migrations.sh"
if [ -f "$MIGRATION_FILE" ]; then
    chmod +x "$MIGRATION_FILE"
    /bin/bash "$MIGRATION_FILE"
fi

echo "Collecting static files"
python manage.py collectstatic --noinput

echo "Starting Gunicorn"
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gthread \
    --threads 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

exec "$@"
