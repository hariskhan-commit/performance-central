#!/usr/bin/env bash
set -euo pipefail

function log { echo "[$(date -Iseconds)] $*"; }

# Leader election for migrations using Redis lock
if [[ "${RUN_MIGRATIONS_ON_BOOT:-false}" == "true" ]]; then
  log "Attempting leader election for migrations..."
  if redis-cli -u "${REDIS_URL}" SET migration_lock "$$" NX EX 60; then
    log "Acquired lock - Waiting for Postgres …"
    /usr/local/bin/wait-for-it.sh "${DATABASE_HOST:-db}:5432" -s -t 60
    log "Running Alembic migrations"
    alembic upgrade head
    redis-cli -u "${REDIS_URL}" DEL migration_lock
  else
    log "Another instance is running migrations - skipping."
  fi
fi

exec "$@"