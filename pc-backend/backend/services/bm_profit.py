from sqlalchemy import select, func, nullif
from backend.models.aggregated import KPIDailySnapshot
from backend.models.core import BMProfitAssumption, BusinessManagerConfig
from sqlalchemy.ext.asyncio import AsyncSession

async def get_profit_summary(session: AsyncSession, start_date, end_date, bm_ids=None):
    kpi_sq = (
        select(
            KPIDailySnapshot.bm_id,
            func.sum(KPIDailySnapshot.revenue).label("revenue"),
            func.sum(KPIDailySnapshot.ad_spend).label("ad_spend"),
        )
        .filter(KPIDailySnapshot.date.between(start_date, end_date))
        .group_by(KPIDailySnapshot.bm_id)
        .subquery()
    )

    stmt = (
        select(
            BusinessManagerConfig.id.label("bm_id"),
            BusinessManagerConfig.name.label("bm_name"),
            kpi_sq.c.revenue,
            kpi_sq.c.ad_spend,
            BMProfitAssumption.profit_margin_pct,
            BMProfitAssumption.fixed_costs,
            BMProfitAssumption.variable_costs_pct,
            (
                (kpi_sq.c.revenue * BMProfitAssumption.profit_margin_pct / 100)
                - BMProfitAssumption.fixed_costs
                - (kpi_sq.c.ad_spend)
            ).label("net_profit"),
            (
                (kpi_sq.c.revenue * BMProfitAssumption.profit_margin_pct / 100)
                / nullif(kpi_sq.c.ad_spend, 0)
            ).label("adjusted_roas"),
        )
        .join(kpi_sq, kpi_sq.c.bm_id == BusinessManagerConfig.id)
        .join(BMProfitAssumption, BMProfitAssumption.bm_id == BusinessManagerConfig.id)
        .filter(BusinessManagerConfig.deleted_at.is_(None), BusinessManagerConfig.is_active == True)
        .filter(BusinessManagerConfig.id.in_(bm_ids) if bm_ids else True)
        .order_by(func.desc("adjusted_roas"))
    )
    return (await session.execute(stmt)).all()