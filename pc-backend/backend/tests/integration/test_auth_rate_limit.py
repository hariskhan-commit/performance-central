import pytest
from flask.testing import FlaskClient

def test_rate_limit_exceeded(client: FlaskClient):
    for _ in range(11):  # Limit is 10/minute
        rv = client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "wrong"})
    assert rv.status_code == 429
    assert "rate limit exceeded" in rv.json.get("error", "").lower()