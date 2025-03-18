#!/bin/bash

# Export all current environment variables to a file so cron jobs can use them
printenv | grep -E 'DATABASE_URL|CLERK_SECRET_KEY' | sed 's/^/export /' > /etc/cron.env

# Run migrations
python -m alembic upgrade head

# Start cron service
service cron start

# Start the main application
exec python -m src.server --prod
