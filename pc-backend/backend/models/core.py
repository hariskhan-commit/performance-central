import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime, Enum, DECIMAL, func, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.asyncio import AsyncAttrs
from . import Base

class StoreType(enum.Enum):
    MASTER = "MASTER"
    CHILD = "CHILD"
    UNKNOWN = "UNKNOWN"

class MetaTokenStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    EXPIRING = "EXPIRING"
    INVALID = "INVALID"

class FetchStatus(enum.Enum):
    PENDING = "PENDING"
    OK = "OK"
    ERROR = "ERROR"

class Region(Base, AsyncAttrs):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    currency_code = Column(String(3), nullable=False)
    is_default = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)

class ProductCategory(Base, AsyncAttrs):
    __tablename__ = "product_categories"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(80), unique=True, nullable=False)
    description = Column(String(512))
    is_default = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base, AsyncAttrs):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(120))
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    totp_secret = Column(LargeBinary)  # Encrypted
    mfa_enabled = Column(Boolean, default=False, nullable=False)

class MasterStoreConfig(Base, AsyncAttrs):
    __tablename__ = "master_store_configs"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    shopify_domain = Column(String(255), unique=True, nullable=False)
    store_type = Column(Enum(StoreType), nullable=False)
    shopify_store_id = Column(String(32))
    api_access_token = Column(String(255))
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BusinessManagerConfig(Base, AsyncAttrs):
    __tablename__ = "business_manager_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_store_id = Column(UUID(as_uuid=True), ForeignKey("master_store_configs.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    child_shopify_domain = Column(String(255), unique=True, nullable=False)
    meta_bm_id = Column(String(50), unique=True, nullable=False)
    meta_app_id_used = Column(String(50))
    meta_user_access_token_reference = Column(String(255))
    meta_token_expires_at = Column(DateTime(timezone=False))
    meta_token_status = Column(Enum(MetaTokenStatus), nullable=False, index=True)
    meta_user_agent_list = Column(Text)
    random_delay_min_seconds = Column(Float)
    random_delay_max_seconds = Column(Float)
    suggested_cron_schedule_notes = Column(Text)
    meta_fetcher_function_name_do = Column(String(100))
    shopify_fetcher_function_name_do = Column(String(100))
    meta_token_last_refreshed_at = Column(DateTime(timezone=False))
    shopify_token_last_refreshed_at = Column(DateTime(timezone=False))
    bm_identifier_custom = Column(String(255))
    has_active_meta_campaigns = Column(Boolean, nullable=False)
    current_product_category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="RESTRICT", onupdate="CASCADE"), index=True)
    last_successful_fetch_meta_at = Column(DateTime(timezone=False))
    last_successful_fetch_shopify_at = Column(DateTime(timezone=False))
    last_fetch_status_meta = Column(Enum(FetchStatus))
    last_fetch_status_shopify = Column(Enum(FetchStatus))
    last_error_message_meta = Column(Text)
    last_error_message_shopify = Column(Text)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

class BMProfitAssumption(Base, AsyncAttrs):
    __tablename__ = "bm_profit_assumptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bm_id = Column(Integer, ForeignKey("business_manager_configs.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    profit_margin_pct = Column(Float, nullable=False)
    fixed_costs = Column(DECIMAL(precision=10, scale=2), nullable=False)
    variable_costs_pct = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())