import pytest
from datetime import date
from backend.models.transactional import ShopifyDailySalesSummary
from backend.models.aggregated import MasterStoreDailySummary
from backend.tasks.tasks import aggregate_master_store_daily_summary

@pytest.mark.asyncio
async def test_aggregate_master_store(db_session, master_store_factory):
    master = await master_store_factory()
    today = date.today()
    sales = ShopifyDailySalesSummary(master_store_id=master.id, summary_date=today, orders_count=10, gross_sales_raw=1000.0, currency_code="USD")
    db_session.add(sales)
    await db_session.commit()

    await aggregate_master_store_daily_summary({"master_store_id": master.id, "date": today.isoformat(), "currency_code": "USD"})

    summary = (await db_session.execute(select(MasterStoreDailySummary).filter_by(master_store_id=master.id, date=today))).scalars().first()
    assert summary.total_revenue == 1000.0