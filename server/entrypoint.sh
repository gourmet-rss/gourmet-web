#!/bin/bash

# Export all current environment variables to a file so cron jobs can use them
printenv | grep -E 'DATABASE_URL|CLERK_SECRET_KEY' | sed 's/^/export /' > /etc/cron.env

# Run migrations
exit_code=$(python -m alembic upgrade head)

if [ $exit_code -ne 0 ]; then
  echo "Failed to run migrations"
  exit $exit_code
fi

# Start cron service
service cron start

# Start the main application
exec python -m src.server --prod
