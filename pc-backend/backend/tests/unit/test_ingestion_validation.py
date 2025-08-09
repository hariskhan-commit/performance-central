import pytest
from marshmallow import ValidationError
from backend.schemas.ingestion import IngestionPayload

def test_valid_payload():
    payload = {"bm_id": 1, "date": "2025-08-05", "data_type": "meta", "payload": {"key": "value"}}
    assert IngestionPayload().load(payload) == payload

def test_invalid_data_type():
    payload = {"bm_id": 1, "date": "2025-08-05", "data_type": "invalid", "payload": {}}
    with pytest.raises(ValidationError):
        IngestionPayload().load(payload)

def test_missing_field():
    payload = {"bm_id": 1, "date": "2025-08-05", "data_type": "meta"}
    with pytest.raises(ValidationError):
        IngestionPayload().load(payload)