from sqlalchemy import select
from backend.models.transactional import MetaCampaignData
from backend.models.core import BusinessManagerConfig
from sqlalchemy.ext.asyncio import AsyncSession

async def get_meta_campaign_rows(session: AsyncSession, start_date, end_date, filters):
    stmt = select(MetaCampaignData).filter(
        MetaCampaignData.date.between(start_date, end_date)
    )
    if filters.get("bm_ids"):
        stmt = stmt.join(
            BusinessManagerConfig,
            BusinessManagerConfig.meta_bm_id == MetaCampaignData.campaign_id
        ).filter(BusinessManagerConfig.id.in_(filters["bm_ids"]))
    if filters.get("campaign_ids"):
        stmt = stmt.filter(MetaCampaignData.campaign_id.in_(filters["campaign_ids"]))
    return (await session.execute(stmt.order_by(MetaCampaignData.date, MetaCampaignData.campaign_id))).scalars().all()