from sqlalchemy import select, func
from backend.models.transactional import MetaDailyPerformance, MetaCampaignData
from backend.models.core import BusinessManagerConfig
from sqlalchemy.ext.asyncio import AsyncSession

async def get_campaign_command_data(session: AsyncSession, start_date, end_date, filters):
    stmt = select(
        MetaCampaignData.campaign_id,
        MetaCampaignData.name,
        MetaCampaignData.status,
        func.sum(MetaDailyPerformance.spend_raw).label("spend_raw"),
        func.sum(MetaDailyPerformance.purchase_conversion_value_meta_raw).label("purchase_conversion_value_meta_raw"),
        func.avg(MetaDailyPerformance.clicks).label("avg_clicks"),
    ).join(MetaDailyPerformance, MetaDailyPerformance.campaign_id == MetaCampaignData.campaign_id
    ).filter(MetaDailyPerformance.date.between(start_date, end_date)
    ).group_by(MetaCampaignData.campaign_id, MetaCampaignData.name, MetaCampaignData.status)

    if filters.get("status"):
        stmt = stmt.filter(MetaCampaignData.status == filters["status"])
    if filters.get("bm_ids"):
        stmt = stmt.join(BusinessManagerConfig).filter(BusinessManagerConfig.id.in_(filters["bm_ids"]))

    return stmt

async def get_campaign_command_totals(session: AsyncSession, start_date, end_date, filters):
    stmt = select(
        func.sum(MetaDailyPerformance.spend_raw).label("total_spend"),
        func.sum(MetaDailyPerformance.purchase_conversion_value_meta_raw).label("total_revenue"),
    ).filter(MetaDailyPerformance.date.between(start_date, end_date))

    if filters.get("bm_ids"):
        stmt = stmt.join(BusinessManagerConfig).filter(BusinessManagerConfig.id.in_(filters["bm_ids"]))

    return (await session.execute(stmt)).first()