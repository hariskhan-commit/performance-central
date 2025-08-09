#!/usr/bin/env bash
# RUN_MIGRATIONS is intentionally false here
export RUN_MIGRATIONS=false
exec celery -A backend.tasks worker --loglevel=info -P solo "$@"