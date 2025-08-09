from flask import Blueprint, request, jsonify
from backend.tasks.tasks import process_master_store_ingestion
from backend.utils.security import require_api_key
from backend.config import Config

ingest_ms_bp = Blueprint('ingest_ms', __name__, url_prefix='/api/v1/ingest_master_store')

@ingest_ms_bp.route('', methods=['POST'])
@require_api_key({"ingest_master"}) if Config.ENABLE_API_KEYS else lambda f: f
async def ingest_master_store():
    data = request.json
    task = process_master_store_ingestion.delay(data)
    return jsonify({"message": "Data accepted", "task_id": task.id}), 202