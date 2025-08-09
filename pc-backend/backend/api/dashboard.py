from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from backend.services.campaign_command import get_campaign_command_data
from backend.utils.pagination import paginate
from backend.utils.db import get_db_session

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')

@dashboard_bp.route('/campaign_command_data', methods=['GET'])
@jwt_required()
async def campaign_command_data():
    start_date = date.fromisoformat(request.args.get('start_date'))
    end_date = date.fromisoformat(request.args.get('end_date'))
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    filters = {k: request.args.getlist(k) for k in ('master_store_ids', 'bm_ids', 'status')}
    async with get_db_session() as session:
        stmt = await get_campaign_command_data(session, start_date, end_date, filters)
        items, pagination = await paginate(session, stmt, page, page_size)
        return jsonify({"rows": [item._asdict() for item in items], "pagination": pagination}), 200