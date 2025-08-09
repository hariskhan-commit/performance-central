#!/usr/bin/env bash
exec gunicorn backend:create_app --factory -w "${WEB_CONCURRENCY:-4}" -k gevent \
     --bind 0.0.0.0:5000 --max-requests 1000 --max-requests-jitter 50 \
     --timeout "${GUNICORN_TIMEOUT:-60}" --preload --access-logfile - "$@"