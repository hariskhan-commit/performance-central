import json
import hashlib
from functools import wraps
from redis.exceptions import ConnectionError
from flask import current_app, jsonify

def redis_cached(timeout=300):
    def decorator(fn):
        @wraps(fn)
        def inner(*a, **kw):
            key = f"cache:{fn.__name__}:{hashlib.md5(str((a,kw)).encode()).hexdigest()}"
            try:
                if (blob := current_app.redis.get(key)):
                    cached = json.loads(blob)
                    return jsonify(cached["body"]), cached["code"]
            except ConnectionError:
                current_app.logger.warning("Redis down – bypassing cache.")
            rv = fn(*a, **kw)
            if rv.status_code < 300:
                try:
                    payload = {"code": rv.status_code, "body": rv.get_json()}
                    current_app.redis.setex(key, timeout, json.dumps(payload))
                except ConnectionError:
                    pass
            return rv
        return inner
    return decorator