#!/bin/bash

# Export all current environment variables to a file so cron jobs can use them
printenv | grep -E 'DATABASE_URL|CLERK_SECRET_KEY' | sed 's/^/export /' > /etc/cron.env

echo "Running migrations..."
echo "DATABASE_URL: ${DATABASE_URL}"

# Run migrations
python -m alembic upgrade head
exit_code=$?

if [ "$exit_code" -ne 0 ]; then
  echo "Failed to run migrations"
  exit $exit_code
fi

echo "Migrations completed successfully"

echo "Starting cron service..."

# Start cron service
service cron start

echo "Starting main application..."

# Start the main application
exec python -m src.server --prod
