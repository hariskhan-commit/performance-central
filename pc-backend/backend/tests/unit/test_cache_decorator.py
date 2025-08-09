import pytest
from unittest.mock import patch
from backend.utils.caching import redis_cached
from flask import Flask, jsonify

app = Flask(__name__)

@redis_cached(timeout=1)
def cached_func():
    return jsonify({"data": "value"}), 200

@pytest.fixture
def client():
    return app.test_client()

@patch('backend.utils.caching.current_app.redis')
def test_cache_hit(mock_redis, client):
    mock_redis.get.return_value = '{"code": 200, "body": {"data": "value"}}'
    with app.app_context():
        rv = cached_func()
    assert rv.json == {"data": "value"}
    assert rv.status_code == 200

@patch('backend.utils.caching.current_app.redis', side_effect=ConnectionError)
def test_cache_bypass_on_error(mock_redis, client):
    with app.app_context():
        rv = cached_func()
    assert rv.json == {"data": "value"}
    assert rv.status_code == 200