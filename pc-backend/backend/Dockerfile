# Multi-stage build for slimmer image

# Build stage
FROM python:3.12 AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run stage
FROM python:3.12-slim AS runtime

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

COPY --from=builder --chown=app:app /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=app:app /usr/local/bin /usr/local/bin

# Optimized copy for better layer caching: copy backend source separately
COPY backend /app/backend

# Copy scripts
COPY docker/*.sh /usr/local/bin/
COPY backend/scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh

# Change ownership and switch user
RUN chown -R app:app /app
USER app

ENTRYPOINT ["docker-entrypoint.sh"]
# Default command can be overridden by docker-compose
CMD ["start-web"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/v1/healthz || exit 1