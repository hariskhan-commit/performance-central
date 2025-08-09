from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import date
from backend.services.category_summary import get_category_summary
from backend.utils.db import get_db_session

cat_bp = Blueprint('cat_summary', __name__, url_prefix='/api/v1/category_summary')

@cat_bp.route('', methods=['GET'])
@jwt_required()
async def category_summary():
    start_date = date.fromisoformat(request.args.get('start_date'))
    end_date = date.fromisoformat(request.args.get('end_date'))
    product_category_ids = request.args.getlist('product_category_ids')
    mode = request.args.get('mode', 'native')
    async with get_db_session() as session:
        rows = await get_category_summary(session, start_date, end_date, product_category_ids, mode)
        return jsonify([r._asdict() for r in rows]), 200