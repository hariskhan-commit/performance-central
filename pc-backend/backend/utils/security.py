import hashlib
import hmac
from datetime import datetime
from functools import wraps
from flask import request, abort, current_app, g
from flask_jwt_extended import get_jwt
from backend.models.security import ApiKey
from backend.utils.db import get_db_session
from bcrypt import checkpw

def require_api_key(required_scopes: set[str]):
    def wrapper(fn):
        @wraps(fn)
        def inner(*a, **kw):
            token = request.headers.get("X-Api-Key", "")
            if not token:
                legacy_token = request.headers.get("X-Ingestion-Token", "")
                if legacy_token == current_app.config['INGESTION_TOKEN']:
                    return fn(*a, **kw)
                abort(401, "API key required")
            kid, _, secret = token.partition(".")
            with get_db_session() as session:
                key_obj = current_app.redis.get(f"ak:{kid}")
                if key_obj:
                    key_dict = json.loads(key_obj)
                    key_obj = ApiKey(key_hash=key_dict['key_hash'], expires_at=datetime.fromisoformat(key_dict['expires_at']), scopes=key_dict['scopes'])
                else:
                    key_obj = session.query(ApiKey).filter_by(key_id=kid, revoked=False).first()
                    if key_obj:
                        current_app.redis.setex(f"ak:{kid}", int((key_obj.expires_at - datetime.utcnow()).total_seconds()), json.dumps({'key_hash': key_obj.key_hash, 'expires_at': str(key_obj.expires_at), 'scopes': key_obj.scopes}))
                if not key_obj or datetime.utcnow() > key_obj.expires_at:
                    grace = current_app.redis.get(f"ak_grace:{kid}")
                    if grace:
                        grace_dict = json.loads(grace)
                        key_obj = ApiKey(key_hash=grace_dict['key_hash'], expires_at=datetime.fromisoformat(grace_dict['expires_at']))
                    else:
                        abort(401, "Invalid key")
                if not required_scopes.issubset(set(key_obj.scopes)):
                    abort(403, "Scope insufficient")
                if checkpw(secret.encode(), key_obj.key_hash.encode()):
                    key_obj.last_used_at = datetime.utcnow()
                    session.commit()
                    return fn(*a, **kw)
                abort(401, "Invalid key")
        return inner
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, "Admin required")
        return fn(*args, **kwargs)
    return wrapper

def mfa_verified(level="totp"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if not claims.get('mfa'):
                abort(403, "MFA required")
            if level == "webauthn" and claims.get('auth') != "webauthn":
                abort(403, "WebAuthn required for this action")
            return fn(*args, **kwargs)
        return wrapper
    return decorator