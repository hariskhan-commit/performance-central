#!/bin/bash
# Bootstrap script for local development

set -e

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from example - edit it with your secrets."
fi

source .env

docker-compose up -d

echo "Waiting for services to start..."
sleep 10

echo "Running migrations..."
docker-compose exec app alembic upgrade head

echo "Local environment ready at http://localhost:5000"