from flask import Blueprint, jsonify
from backend.utils.health import compute_health_status, compute_freshness_score
from backend.utils.db import get_db_session

health_bp = Blueprint('health', __name__, url_prefix='/api/v1/system_health')

@health_bp.route('', methods=['GET'])
async def system_health():
    async with get_db_session() as session:
        status = await compute_health_status(session)
        score = await compute_freshness_score(session)
        return jsonify({"status": status, "freshness_score": score}), 200