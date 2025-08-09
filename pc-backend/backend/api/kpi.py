from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from backend.services.kpi import get_kpi_snapshot
from backend.utils.db import get_db_session

kpi_bp = Blueprint('kpi', __name__, url_prefix='/api/v1/kpi')

@kpi_bp.route('/snapshot', methods=['GET'])
@jwt_required()
async def kpi_snapshot():
    start_date = date.fromisoformat(request.args.get('start_date'))
    end_date = date.fromisoformat(request.args.get('end_date'))
    master_store_ids = request.args.getlist('master_store_ids')
    bm_ids = request.args.getlist('bm_ids')
    mode = request.args.get('mode', 'native')
    async with get_db_session() as session:
        rows = await get_kpi_snapshot(session, start_date, end_date, master_store_ids, bm_ids, mode)
        return jsonify([r._asdict() for r in rows]), 200