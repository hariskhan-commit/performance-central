from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from . import Base
from .core import AsyncAttrs

class MetaDailyPerformance(Base, AsyncAttrs):
    __tablename__ = "meta_daily_performance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    spend_raw = Column(DECIMAL(precision=10, scale=2), nullable=False)
    clicks = Column(Integer, nullable=False)
    impressions = Column(Integer, nullable=False)
    results = Column(Integer, nullable=False)
    purchase_conversion_value_meta_raw = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = ({"postgresql_partition_by": "RANGE (date)"},)

class ShopifyDailySalesSummary(Base, AsyncAttrs):
    __tablename__ = "shopify_daily_sales_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    master_store_id = Column(UUID(as_uuid=True), ForeignKey("master_store_configs.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    summary_date = Column(Date, nullable=False)
    orders_count = Column(Integer, nullable=False)
    gross_sales_raw = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ShopifyChildDailySalesSummary(Base, AsyncAttrs):
    __tablename__ = "shopify_child_daily_sales_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bm_id = Column(Integer, ForeignKey("business_manager_configs.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    summary_date = Column(Date, nullable=False)
    orders_count = Column(Integer, nullable=False)
    gross_sales_raw = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetaCampaignData(Base, AsyncAttrs):
    __tablename__ = "meta_campaign_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    ad_budget = Column(DECIMAL(precision=10, scale=2), nullable=False)
    reach = Column(Integer, nullable=False)
    landing_page_views = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())