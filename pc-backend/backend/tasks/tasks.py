from datetime import date, datetime
from celery import chord
from backend.tasks import app
from backend.utils.db import get_db_session
from backend.models.transactional import MetaDailyPerformance, ShopifyChildDailySalesSummary, ShopifyDailySalesSummary
from backend.models.aggregated import MasterStoreDailySummary, KPIDailySnapshot
from sqlalchemy import select, func
from flask import current_app

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, rate_limit='10/m')
def process_ingestion(self, data):
    with get_db_session() as session:
        try:
            if data["data_type"] == "meta":
                for entry in data["payload"]:
                    perf = MetaDailyPerformance(
                        campaign_id=entry["campaign_id"],
                        date=date.fromisoformat(data["date"]),
                        spend_raw=entry["spend"],
                        clicks=entry["clicks"],
                        impressions=entry["impressions"],
                        results=entry.get("results", 0),
                        purchase_conversion_value_meta_raw=entry.get("purchase_value", 0),
                        currency_code=entry.get("currency_code", "USD")
                    )
                    session.merge(perf)
                session.commit()
                aggregate_master_store_daily_summary.delay(data)  # Full data
            elif data["data_type"] == "shopify_child":
                summary = ShopifyChildDailySalesSummary(
                    bm_id=data["bm_id"],
                    summary_date=date.fromisoformat(data["date"]),
                    orders_count=data["payload"]["orders_count"],
                    gross_sales_raw=data["payload"]["gross_sales"],
                    currency_code=data["payload"].get("currency_code", "USD")
                )
                session.merge(summary)
                session.commit()
                upsert_kpi_daily_snapshot.delay(data["bm_id"], data["date"])
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def process_master_store_ingestion(self, data):
    with get_db_session() as session:
        try:
            summary = ShopifyDailySalesSummary(
                master_store_id=data["master_store_id"],
                summary_date=date.fromisoformat(data["date"]),
                orders_count=data["payload"]["orders_count"],
                gross_sales_raw=data["payload"]["gross_sales"],
                currency_code=data["payload"].get("currency_code", "USD")
            )
            session.merge(summary)
            session.commit()
            aggregate_master_store_daily_summary.delay(data)
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def aggregate_master_store_daily_summary(self, data):
    with get_db_session() as session:
        try:
            master_id = data["master_store_id"]
            day = date.fromisoformat(data["date"])
            revenue = session.query(func.sum(ShopifyDailySalesSummary.gross_sales_raw)).filter_by(
                master_store_id=master_id, summary_date=day
            ).scalar() or 0.0
            ad_spend = session.query(func.sum(MetaDailyPerformance.spend_raw)).filter_by(
                date=day
            ).scalar() or 0.0
            currency = data.get("currency_code", "USD")
            summary = MasterStoreDailySummary(
                master_store_id=master_id,
                date=day,
                total_revenue=revenue,
                total_ad_spend=ad_spend,
                currency_code=currency
            )
            session.merge(summary)
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def upsert_kpi_daily_snapshot(self, bm_id, date_str):
    day = date.fromisoformat(date_str)
    with get_db_session() as session:
        try:
            revenue = session.query(func.sum(ShopifyChildDailySalesSummary.gross_sales_raw)).filter_by(
                bm_id=bm_id, summary_date=day
            ).scalar() or 0.0
            ad_spend = session.query(func.sum(MetaDailyPerformance.spend_raw)).filter_by(
                date=day
            ).scalar() or 0.0
            roas = revenue / ad_spend if ad_spend > 0 else 0.0
            cpa = ad_spend / (revenue / 100) if revenue > 0 else 0.0
            currency = "USD"
            snapshot = KPIDailySnapshot(
                bm_id=bm_id,
                date=day,
                revenue=revenue,
                ad_spend=ad_spend,
                roas=roas,
                cpa=cpa,
                currency_code=currency
            )
            session.merge(snapshot)
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)