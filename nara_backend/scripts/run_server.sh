#!/bin/sh

# Change to the directory containing manage.py (we're already in /app/nara_backend)
cd /app/nara_backend

# Run migrations
MIGRATION_FILE="scripts/run_migrations.sh"
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