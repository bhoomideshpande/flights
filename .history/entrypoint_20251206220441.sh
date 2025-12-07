#!/bin/sh
set -e

# Ensure environment variables are available
echo "Running migrations and collecting static files..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start the application
exec "$@"
