#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
cd /app/app/db && PYTHONPATH=/app alembic upgrade head

# Start the application
echo "Starting application..."
cd /app
exec "$@"