# Performance Central v25 — Backend

Flask 3 + SQLAlchemy 2 (async), Celery, Redis, Postgres, Prometheus, OpenTelemetry, JWT/TOTP/Passkeys, and API‑key management — all wired up and ready to ship.

- **API root:** `/api/v1`
- **Docs:** `GET /docs` (Swagger UI) → loads `/docs/openapi.yaml`
- **Health:** `GET /api/v1/healthz`
- **Version:** `GET /api/v1/version`

---

## Quick start (Docker)

> Requires Docker and Docker Compose v2.

```bash
cd backend

# 1) Create local env file from the example
cp .env.example .env
# Edit secrets: SECRET_KEY, JWT_SECRET_KEY, INGESTION_TOKEN, TOTP_ENCRYPTION_KEY, etc.

# 2) Build & start
docker compose up -d --build

# 3) Apply DB migrations (one time or after schema changes)
docker compose exec app alembic upgrade head

# 4) Visit:
# API       http://localhost:5000/api/v1/status
# Docs      http://localhost:5000/docs
# Flower    http://localhost:5555 (Celery)
