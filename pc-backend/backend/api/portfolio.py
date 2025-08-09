from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.services.portfolio import get_bm_health_rows
from backend.utils.db import get_db_session

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/v1/portfolio')

@portfolio_bp.route('/snapshot', methods=['GET'])
@jwt_required()
async def portfolio_snapshot():
    region_ids = request.args.getlist('region_ids')
    master_store_ids = request.args.getlist('master_store_ids')
    async with get_db_session() as session:
        rows = await get_bm_health_rows(session, region_ids, master_store_ids)
        return jsonify([r._asdict() for r in rows]), 200