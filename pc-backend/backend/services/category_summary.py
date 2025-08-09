from sqlalchemy import select, func
from backend.models.aggregated import KPIDailySnapshot
from backend.models.core import ProductCategory
from backend.utils.fx_conversion import bulk_convert
from sqlalchemy.ext.asyncio import AsyncSession

async def get_category_summary(session: AsyncSession, start_date, end_date, product_category_ids=None, mode="native"):
    stmt = select(
        ProductCategory.name,
        func.sum(KPIDailySnapshot.revenue).label("total_revenue"),
        func.sum(KPIDailySnapshot.ad_spend).label("total_ad_spend"),
    ).join(ProductCategory).filter(
        KPIDailySnapshot.date.between(start_date, end_date)
    ).group_by(ProductCategory.name)

    if product_category_ids:
        stmt = stmt.filter(ProductCategory.id.in_(product_category_ids))

    rows = (await session.execute(stmt)).all()
    if mode == "usd":
        await bulk_convert(session, [r._asdict() for r in rows], ("total_revenue", "total_ad_spend"), "date", "currency_code")
    return rows