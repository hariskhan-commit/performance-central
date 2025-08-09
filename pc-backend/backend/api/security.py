import secrets
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from pyotp import TOTP, random_base32
from cryptography.fernet import Fernet
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import PublicKeyCredentialCreationOptions, PublicKeyCredentialRequestOptions
from backend.models.security import ApiKey, WebAuthnCredential
from backend.models.core import User
from backend.utils.db import get_db_session
from backend.utils.security import mfa_verified, admin_required
from bcrypt import hashpw, gensalt

security_bp = Blueprint('security', __name__, url_prefix='/api/v1/security')

@security_bp.route('/totp/enroll', methods=['POST'])
@jwt_required()
async def totp_enroll():
    identity = get_jwt()['sub']
    async with get_db_session() as session:
        user = await session.get(User, identity)
        if not user:
            return jsonify({"error": "User not found"}), 404
        secret = random_base32()
        f = Fernet(Config.TOTP_ENCRYPTION_KEY)
        user.totp_secret = f.encrypt(secret.encode())
        await session.commit()
        uri = TOTP(secret).provisioning_uri(user.email, issuer_name="Performance Central")
        return jsonify({"otpauth_uri": uri}), 200

@security_bp.route('/totp/verify', methods=['POST'])
@jwt_required()
async def totp_verify():
    identity = get_jwt()['sub']
    code = request.json.get('code')
    async with get_db_session() as session:
        user = await session.get(User, identity)
        if not user or not user.totp_secret:
            return jsonify({"error": "Enrollment not started"}), 400
        f = Fernet(Config.TOTP_ENCRYPTION_KEY)
        secret = f.decrypt(user.totp_secret).decode()
        totp = TOTP(secret)
        if totp.verify(code, valid_window=1):
            user.mfa_enabled = True
            await session.commit()
            return jsonify({"message": "MFA enabled"}), 200
        return jsonify({"error": "Invalid code"}), 400

@security_bp.route('/passkeys/register/challenge', methods=['GET'])
@jwt_required()
async def passkey_register_challenge():
    identity = get_jwt()['sub']
    options = generate_registration_options(
        rp_id="localhost",
        rp_name="Performance Central",
        user_id=str(identity),
        user_name="user",
        timeout=60000
    )
    current_app.redis.setex(f"webauthn_challenge:{identity}", 300, options.challenge)
    return jsonify(options.dict()), 200

@security_bp.route('/passkeys/register/verify', methods=['POST'])
@jwt_required()
async def passkey_register_verify():
    identity = get_jwt()['sub']
    response = request.json
    challenge = current_app.redis.get(f"webauthn_challenge:{identity}")
    if not challenge:
        return jsonify({"error": "Challenge expired"}), 400
    verification = verify_registration_response(
        credential=response,
        expected_challenge=challenge,
        expected_rp_id="localhost",
        expected_origin="http://localhost"
    )
    async with get_db_session() as session:
        cred = WebAuthnCredential(
            user_id=identity,
            cred_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count
        )
        session.add(cred)
        await session.commit()
    current_app.redis.delete(f"webauthn_challenge:{identity}")
    return jsonify({"message": "Passkey registered"}), 200

@security_bp.route('/passkeys/auth/challenge', methods=['GET'])
async def passkey_auth_challenge():
    email = request.args.get('email')
    async with get_db_session() as session:
        user = (await session.execute(select(User).filter_by(email=email))).scalars().first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        creds = (await session.execute(select(WebAuthnCredential).filter_by(user_id=user.id))).scalars().all()
        allowed_cred_ids = [c.cred_id for c in creds]
        options = generate_authentication_options(
            rp_id="localhost",
            allow_credentials=allowed_cred_ids,
            timeout=60000
        )
        current_app.redis.setex(f"webauthn_auth_challenge:{user.id}", 300, options.challenge)
        return jsonify(options.dict()), 200

@security_bp.route('/passkeys/auth/verify', methods=['POST'])
async def passkey_auth_verify():
    data = request.json
    user_id = data['user_id']
    response = data['assertion']
    challenge = current_app.redis.get(f"webauthn_auth_challenge:{user_id}")
    if not challenge:
        return jsonify({"error": "Challenge expired"}), 400
    async with get_db_session() as session:
        cred = (await session.execute(select(WebAuthnCredential).filter_by(cred_id=response['id']))).scalars().first()
        if not cred:
            return jsonify({"error": "Credential not found"}), 404
        verification = verify_authentication_response(
            credential=response,
            expected_challenge=challenge,
            expected_rp_id="localhost",
            expected_origin="http://localhost",
            credential_public_key=cred.public_key,
            credential_current_sign_count=cred.sign_count
        )
        cred.sign_count = verification.new_sign_count
        await session.commit()
    current_app.redis.delete(f"webauthn_auth_challenge:{user_id}")
    access_token = create_access_token(identity=user_id, additional_claims={"mfa": True, "auth": "webauthn"})
    return jsonify({"access_token": access_token}), 200

@security_bp.route('/admin/api_keys', methods=['GET'])
@jwt_required()
@admin_required
@mfa_verified
async def list_api_keys():
    status = request.args.get('status')
    owner = request.args.get('owner')
    bm_id = request.args.get('bm_id')
    async with get_db_session() as session:
        stmt = select(ApiKey)
        if status:
            stmt = stmt.filter(ApiKey.revoked == (status == 'revoked'))
        if owner:
            stmt = stmt.filter(ApiKey.owner_user_id == owner)
        if bm_id:
            stmt = stmt.filter(ApiKey.bm_id == bm_id)
        keys = (await session.execute(stmt)).scalars().all()
        return jsonify([{"key_id": k.key_id, "scopes": k.scopes, "expires_at": k.expires_at, "revoked": k.revoked} for k in keys]), 200

@security_bp.route('/admin/api_keys', methods=['POST'])
@jwt_required()
@admin_required
@mfa_verified
async def create_api_key():
    data = request.json
    secret = secrets.token_urlsafe(48)
    key_id = f"{data['scopes'][0]}_{secrets.token_hex(6)}"
    salt = gensalt()
    key_hash = hashpw(secret.encode(), salt).decode()
    expires_at = datetime.utcnow() + timedelta(days=data.get('ttl_days', 90))
    async with get_db_session() as session:
        key = ApiKey(
            key_id=key_id,
            key_hash=key_hash,
            scopes=data['scopes'],
            rate_limit=data.get('rate_limit', '60/minute'),
            expires_at=expires_at,
            owner_user_id=get_jwt()['sub'],
            bm_id=data.get('bm_id')
        )
        session.add(key)
        await session.commit()
        current_app.redis.setex(f"ak:{key_id}", int((expires_at - datetime.utcnow()).total_seconds()), json.dumps({'key_hash': key_hash, 'expires_at': str(expires_at), 'scopes': key.scopes}))
        return jsonify({"api_key": f"{key_id}.{secret}"}), 201

@security_bp.route('/admin/api_keys/<uuid:key_id>/rotate', methods=['POST'])
@jwt_required()
@admin_required
@mfa_verified
async def rotate_api_key(key_id):
    async with get_db_session() as session:
        key = (await session.execute(select(ApiKey).filter_by(id=key_id))).scalars().first()
        if not key:
            return jsonify({"error": "Key not found"}), 404
        key.revoked = True
        await session.commit()
        new_data = {"scopes": key.scopes, "ttl_days": (key.expires_at - datetime.utcnow()).days, "bm_id": key.bm_id, "rate_limit": key.rate_limit}
        response = await create_api_key(new_data)
        current_app.redis.setex(f"ak_grace:{key.key_id}", Config.KEY_GRACE_HOURS * 3600, json.dumps({'key_hash': key.key_hash, 'expires_at': str(key.expires_at)}))
        return response

@security_bp.route('/admin/api_keys/<uuid:key_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@mfa_verified
async def revoke_api_key(key_id):
    async with get_db_session() as session:
        key = (await session.execute(select(ApiKey).filter_by(id=key_id))).scalars().first()
        if not key:
            return jsonify({"error": "Key not found"}), 404
        key.revoked = True
        await session.commit()
        current_app.redis.delete(f"ak:{key.key_id}")
        return '', 204