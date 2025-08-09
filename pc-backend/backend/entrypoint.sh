#!/bin/bash
set -e

echo "Waiting for database to be ready..."
./scripts/wait-for-it.sh db:5432 -t 60 -- echo "Database is ready."

echo "Applying database migrations..."
if alembic current | grep '(head)'; then
  echo "DB already at head – skipping migration."
else
  alembic upgrade head || { echo "Migration failed" ; exit 1; }
fi
echo "Migrations applied successfully."

exec "$@"