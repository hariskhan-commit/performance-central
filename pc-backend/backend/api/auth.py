from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from backend.models.core import User
from backend.utils.db import get_db_session
from backend.schemas.auth import LoginSchema
from pyotp import TOTP
from cryptography.fernet import Fernet

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
async def login():
    schema = LoginSchema()
    data = schema.load(request.json)
    async with get_db_session() as session:
        user = await session.execute(select(User).filter_by(email=data['email'])).scalars().first()
        if not user or not current_app.bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        if user.mfa_enabled and Config.ENABLE_MFA:
            temp_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=5), additional_claims={"mfa_required": True})
            return jsonify({"mfa_required": True, "temp_token": temp_token}), 200
        access_token = create_access_token(identity=user.id, additional_claims={"mfa": False})
        return jsonify({"access_token": access_token}), 200

@auth_bp.route('/mfa/verify', methods=['POST'])
@jwt_required()
async def verify_mfa():
    identity = get_jwt()['sub']
    claims = get_jwt()
    if not claims.get("mfa_required"):
        return jsonify({"error": "MFA not required"}), 400
    code = request.json.get("code")
    async with get_db_session() as session:
        user = await session.get(User, identity)
        if not user or not user.mfa_enabled:
            return jsonify({"error": "MFA not enabled"}), 400
        f = Fernet(Config.TOTP_ENCRYPTION_KEY)
        secret = f.decrypt(user.totp_secret).decode()
        totp = TOTP(secret)
        if totp.verify(code, valid_window=1):
            access_token = create_access_token(identity=identity, additional_claims={"mfa": True})
            return jsonify({"access_token": access_token}), 200
        return jsonify({"error": "Invalid MFA code"}), 401