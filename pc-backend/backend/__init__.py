import os
import logging
import signal
import sys
import gevent.monkey
gevent.monkey.patch_all()

from flask import Flask, jsonify, g, send_from_directory, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from prometheus_flask_exporter import PrometheusMetrics
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import instrument_app
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor  # For async DB

from backend.config import Config
from backend.models import Base
from backend.middleware.request_id import init_app as request_id_init
from backend.utils.logging import init_logging

# Blueprints
from backend.api.auth import auth_bp
from backend.api.v1 import api_v1
from backend.api.ingest import ingest_bp
from backend.api.ingest_master_store import ingest_ms_bp
from backend.api.dashboard import dashboard_bp
from backend.api.portfolio import portfolio_bp
from backend.api.kpi import kpi_bp
from backend.api.export import export_bp
from backend.api.fx_rates import fx_rates_bp
from backend.api.system_health import health_bp
from backend.api.profit_assumptions import profit_bp
from backend.api.category_summary import cat_bp
from backend.api.security import security_bp

bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address, storage_uri=Config.REDIS_URL, default_limits=["100/minute"])
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()
talisman = Talisman()

def create_app(config_object=Config):
    config_object.validate_for_prod()
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_object)

    if app.config['FLASK_DEBUG'] == 0:
        if app.config['SECRET_KEY'] == 'default-secret-key':
            raise ValueError("FATAL: SECRET_KEY must be set to a secure value in production.")
        if app.config['JWT_SECRET_KEY'] == 'jwt-secret-key':
            raise ValueError("FATAL: JWT_SECRET_KEY must be set to a secure value in production.")
        if Config.ENABLE_API_KEYS and app.config['INGESTION_TOKEN'] == 'ingest-token-placeholder':
            raise ValueError("FATAL: INGESTION_TOKEN must be set or migrate to API keys.")

    if app.config['DATABASE_URL'].startswith('sqlite') and app.config['FLASK_DEBUG'] == 0:
        raise ValueError("FATAL: SQLite is not allowed in production environments.")

    bcrypt.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS'), supports_credentials=True)
    jwt.init_app(app)
    metrics.init_app(app)
    talisman.init_app(app, content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' unpkg.com",  # For Swagger
    })

    # Async SQLAlchemy
    engine = create_async_engine(app.config['DATABASE_URL'], echo=False)
    app.async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # OTel with fallback
    try:
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=Config.OTEL_EXPORTER_OTLP_ENDPOINT)))
        instrument_app(app)
        AsyncPGInstrumentor().instrument()  # Async DB
        Jinja2Instrumentor().instrument()
    except Exception as e:
        app.logger.warning(f"OTel instrumentation failed: {e} - proceeding without tracing.")

    if app.config['FLASK_DEBUG']:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    blueprints = [
        auth_bp, api_v1, ingest_bp, ingest_ms_bp, dashboard_bp, portfolio_bp, kpi_bp, export_bp, fx_rates_bp, health_bp, profit_bp, cat_bp, security_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)

    request_id_init(app)
    init_logging(app)

    @app.errorhandler(Exception)
    def handle_exception(err):
        from werkzeug.exceptions import HTTPException
        if isinstance(err, HTTPException):
            response = {"error": err.description, "request_id": g.get('request_id', '-')}
            return jsonify(response), err.code
        
        app.logger.exception("Unhandled internal server error occurred.")
        response = {"error": "Internal Server Error", "request_id": g.get('request_id', '-')}
        return jsonify(response), 500

    @app.route('/api/v1/healthz')
    async def healthz():
        async with app.async_session() as session:
            try:
                await session.execute(select(1))
                try:
                    current_app.redis.ping()
                except:
                    pass  # Graceful
                return jsonify({"status": "healthy"}), 200
            except Exception as e:
                app.logger.error(f"Health check failed: {e}")
                return jsonify({"status": "unhealthy"}), 503

    @app.route('/api/v1/version')
    def version():
        return jsonify({
            "git_sha": os.getenv("GIT_SHA", "unknown"),
            "build_time": os.getenv("BUILD_TIME", "unknown")
        })

    @app.teardown_appcontext
    async def shutdown_session(exception=None):
        if hasattr(g, 'db_session'):
            if exception:
                await g.db_session.rollback()
            else:
                await g.db_session.commit()
            await g.db_session.close()

    app.redis = Redis.from_url(app.config['REDIS_URL'], decode_responses=True)

    def shutdown_handler(signum, frame):
        app.logger.info("Shutdown signal received. Closing connections.")
        if hasattr(app, 'redis'):
            app.redis.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    @app.route('/docs')
    def swagger_ui():
        return render_template('swagger_ui.html')

    @app.route('/docs/openapi.yaml')
    def openapi_spec():
        return send_from_directory(app.root_path, 'openapi.yaml')

    return app