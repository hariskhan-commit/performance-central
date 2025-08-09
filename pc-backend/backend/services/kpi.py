from sqlalchemy import select
from backend.models.aggregated import KPIDailySnapshot
from backend.utils.fx_conversion import bulk_convert
from sqlalchemy.ext.asyncio import AsyncSession

async def get_kpi_snapshot(session: AsyncSession, start_date, end_date, master_store_ids=None, bm_ids=None, mode="native"):
    stmt = select(KPIDailySnapshot).filter(
        KPIDailySnapshot.date.between(start_date, end_date)
    )
    if bm_ids:
        stmt = stmt.filter(KPIDailySnapshot.bm_id.in_(bm_ids))
    rows = (await session.execute(stmt)).scalars().all()
    if mode == "usd":
        await bulk_convert(session, [r._asdict() for r in rows], ("revenue", "ad_spend"), "date", "currency_code")
    return rows