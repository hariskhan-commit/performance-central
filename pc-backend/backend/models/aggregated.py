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