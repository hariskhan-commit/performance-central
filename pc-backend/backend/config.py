import os
from datetime import timedelta

class Config:
    FLASK_DEBUG = int(os.getenv("FLASK_DEBUG", 0))
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 4)))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///performance.db")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", 20)),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
    }
    INGESTION_TOKEN = os.getenv("INGESTION_TOKEN", "ingest-token-placeholder")
    LEGACY_API_KEY = os.getenv("LEGACY_API_KEY", "legacy_token_placeholder")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    RETENTION_MONTHS = int(os.getenv("RETENTION_MONTHS", 24))
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    ENABLE_USD_MODE = os.getenv("ENABLE_USD_MODE", "true").lower() == "true"
    ENABLE_API_KEYS = os.getenv("ENABLE_API_KEYS", "true").lower() == "true"
    ENABLE_MFA = os.getenv("ENABLE_MFA", "true").lower() == "true"
    FX_API_URL = os.getenv("FX_API_URL", "https://api.exchangerate.host")
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 12))
    KEY_GRACE_HOURS = int(os.getenv("KEY_GRACE_HOURS", 4))
    OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    TOTP_ENCRYPTION_KEY = os.getenv("TOTP_ENCRYPTION_KEY", secrets.token_bytes(32))  # KMS in prod

    @classmethod
    def validate_for_prod(cls):
        if cls.FLASK_DEBUG == 0:
            missing = [k for k in ("SECRET_KEY", "JWT_SECRET_KEY") if not getattr(cls, k)]
            if missing:
                raise RuntimeError(f"Mandatory secrets not set: {', '.join(missing)}")
            if cls.BCRYPT_LOG_ROUNDS < 12:
                raise RuntimeError("BCRYPT_LOG_ROUNDS too low for production")
            if "*" in cls.CORS_ORIGINS:
                raise RuntimeError("Wildcard CORS not allowed in production")