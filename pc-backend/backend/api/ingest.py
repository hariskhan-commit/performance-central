from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from backend.tasks.tasks import process_ingestion
from backend.utils.security import require_api_key
from backend.config import Config

ingest_bp = Blueprint('ingest', __name__, url_prefix='/api/v1/ingest')

@ingest_bp.route('', methods=['POST'])
@require_api_key({"ingest"}) if Config.ENABLE_API_KEYS else jwt_required()
async def ingest_data():
    data = request.json
    task = process_ingestion.delay(data)
    return jsonify({"message": "Data accepted", "task_id": task.id}), 202