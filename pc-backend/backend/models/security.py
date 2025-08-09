import json
from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, LargeBinary
from . import Base
from .core import AsyncAttrs

class ApiKey(Base, AsyncAttrs):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    key_hash = Column(String(255), nullable=False, index=True)  # bcrypt
    key_id = Column(String(100), nullable=False, unique=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    bm_id = Column(Integer, ForeignKey("business_manager_configs.id", ondelete="CASCADE", onupdate="CASCADE"))
    scopes = Column(ARRAY(String))
    rate_limit = Column(String, default="60/minute")
    expires_at = Column(DateTime(timezone=True))
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return {
            'id': self.id,
            'key_hash': self.key_hash,
            'key_id': self.key_id,
            'owner_user_id': self.owner_user_id,
            'bm_id': self.bm_id,
            'scopes': self.scopes,
            'rate_limit': self.rate_limit,
            'expires_at': self.expires_at,
            'revoked': self.revoked,
            'created_at': self.created_at,
            'last_used_at': self.last_used_at
        }

class WebAuthnCredential(Base, AsyncAttrs):
    __tablename__ = "webauthn_credentials"
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    cred_id = Column(String, unique=True, nullable=False)
    public_key = Column(LargeBinary, nullable=False)
    sign_count = Column(Integer, nullable=False)
    transports = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())