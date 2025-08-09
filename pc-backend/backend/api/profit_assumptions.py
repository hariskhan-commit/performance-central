from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from backend.services.bm_profit import get_profit_summary
from backend.utils.db import get_db_session

profit_bp = Blueprint('profit', __name__, url_prefix='/api/v1/profit_assumptions')

@profit_bp.route('/summary', methods=['GET'])
@jwt_required()
async def profit_summary():
    start_date = date.fromisoformat(request.args.get('start_date'))
    end_date = date.fromisoformat(request.args.get('end_date'))
    bm_ids = request.args.getlist('bm_ids')
    mode = request.args.get('mode', 'native')
    async with get_db_session() as session:
        rows = await get_profit_summary(session, start_date, end_date, bm_ids)
        return jsonify([r._asdict() for r in rows]), 200