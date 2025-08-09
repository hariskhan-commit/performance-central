from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import date
from backend.models.aggregated import FXDailyRate
from backend.utils.db import get_db_session
from backend.utils.security import admin_required
from sqlalchemy import select

fx_rates_bp = Blueprint('fx_rates', __name__, url_prefix='/api/v1/fx-rates')

@fx_rates_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
async def list_fx_rates():
    currency = request.args.get('currency')
    rate_date = request.args.get('date')
    async with get_db_session() as session:
        stmt = select(FXDailyRate).filter(FXDailyRate.source == 'manual')
        if currency:
            stmt = stmt.filter(FXDailyRate.from_currency == currency.upper())
        if rate_date:
            stmt = stmt.filter(FXDailyRate.date == date.fromisoformat(rate_date))
        rates = (await session.execute(stmt)).scalars().all()
        return jsonify([{"id": r.id, "date": r.date, "from_currency": r.from_currency, "to_currency": r.to_currency, "rate": r.rate, "source": r.source} for r in rates]), 200

@fx_rates_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
async def create_fx_rate():
    data = request.json
    async with get_db_session() as session:
        existing = (await session.execute(select(FXDailyRate).filter_by(date=date.fromisoformat(data['date']), from_currency=data['from_currency'], to_currency=data['to_currency'], source='manual'))).scalars().first()
        if existing:
            return jsonify({"error": "Manual rate already exists"}), 409
        new_rate = FXDailyRate(date=date.fromisoformat(data['date']), from_currency=data['from_currency'], to_currency=data['to_currency'], rate=data['rate'], source='manual')
        session.add(new_rate)
        await session.commit()
        return jsonify({"id": new_rate.id, "date": new_rate.date, "from_currency": new_rate.from_currency, "to_currency": new_rate.to_currency, "rate": new_rate.rate, "source": new_rate.source}), 201

@fx_rates_bp.route('/<int:rate_id>', methods=['PUT'])
@jwt_required()
@admin_required
async def update_fx_rate(rate_id):
    data = request.json
    async with get_db_session() as session:
        rate = (await session.execute(select(FXDailyRate).filter_by(id=rate_id))).scalars().first()
        if not rate:
            return jsonify({"error": "Rate not found"}), 404
        if rate.source != 'manual':
            return jsonify({"error": "Cannot modify auto rate"}), 403
        rate.rate = data['rate']
        await session.commit()
        return jsonify({"id": rate.id, "date": rate.date, "from_currency": rate.from_currency, "to_currency": rate.to_currency, "rate": rate.rate, "source": rate.source}), 200

@fx_rates_bp.route('/<int:rate_id>', methods=['DELETE'])
@jwt_required()
@admin_required
async def delete_fx_rate(rate_id):
    async with get_db_session() as session:
        rate = (await session.execute(select(FXDailyRate).filter_by(id=rate_id))).scalars().first()
        if not rate:
            return jsonify({"error": "Rate not found"}), 404
        if rate.source != 'manual':
            return jsonify({"error": "Cannot delete auto rate"}), 403
        await session.delete(rate)
        await session.commit()
        return '', 204