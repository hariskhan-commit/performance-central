from datetime import datetime
from sqlalchemy import Column, Integer, Date, DECIMAL, Float, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from . import Base
from .core import AsyncAttrs

class MasterStoreDailySummary(Base, AsyncAttrs):
    __tablename__ = "master_store_daily_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_store_id = Column(UUID(as_uuid=True), ForeignKey("master_store_configs.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    total_revenue = Column(DECIMAL(precision=10, scale=2), nullable=False)
    total_ad_spend = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KPIDailySnapshot(Base, AsyncAttrs):
    __tablename__ = "kpi_daily_snapshot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bm_id = Column(Integer, ForeignKey("business_manager_configs.id", ondelete="CASCADE", onupdate="CASCADE"))
    product_category_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id", ondelete="CASCADE", onupdate="CASCADE"))
    date = Column(Date, nullable=False)
    revenue = Column(DECIMAL(precision=10, scale=2), nullable=False)
    ad_spend = Column(DECIMAL(precision=10, scale=2), nullable=False)
    roas = Column(Float, nullable=False)
    cpa = Column(Float, nullable=False)
    currency_code = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FXDailyRate(Base, AsyncAttrs):
    __tablename__ = "fx_daily_rates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(DECIMAL(precision=10, scale=6), nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # --- CCV v2: CampaignCommandSnapshot -----------------------------------------
from sqlalchemy import (
    Column, Integer, Date, DECIMAL, Float, String, ForeignKey, func,
    DateTime, UniqueConstraint
)
from backend.models import Base
from backend.models.core import AsyncAttrs  # keep consistent with your project

class CampaignCommandSnapshot(Base, AsyncAttrs):
    """
    One row per (bm_id, campaign_id, date).
    Stored in UTC (timezone-aware). Local-time display happens in API layer.
    """
    __tablename__ = "campaign_command_snapshot"

    # Composite PK
    bm_id = Column(Integer, ForeignKey("business_manager_configs.id", ondelete="CASCADE"), primary_key=True)
    campaign_id = Column(String(50), primary_key=True)
    date = Column(Date, primary_key=True)

    # Cached dims
    bm_name = Column(String(100), nullable=False)
    master_store_id = Column(String(36), nullable=False)
    master_store_name = Column(String(120), nullable=False)

    # Campaign attrs
    campaign_name = Column(String(255), nullable=False)
    campaign_status = Column(String(50), nullable=False)  # ACTIVE|PAUSED|...
    currency_code = Column(String(3), nullable=False)

    # Core metrics
    ad_budget = Column(DECIMAL(12, 2))
    spend_raw = Column(DECIMAL(12, 2))
    shopify_orders = Column(Integer)
    shopify_revenue = Column(DECIMAL(12, 2))
    clicks = Column(Integer)
    impressions = Column(Integer)
    landing_page_views = Column(Integer)
    results = Column(Integer)
    purchase_conversion_value_meta_raw = Column(DECIMAL(12, 2))

    # Derived metrics
    ad_budget_spend_pct = Column(Float)
    true_roas = Column(Float)
    aov = Column(Float)
    ctr_link = Column(Float)
    cost_per_lpv = Column(Float)

    # Timestamps (UTC)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('bm_id', 'campaign_id', 'date', name='uq_campaign_command_snapshot_key'),
    )
