from datetime import datetime
from sqlalchemy import select, func
from backend.models.core import BusinessManagerConfig, MasterStoreConfig
from sqlalchemy.ext.asyncio import AsyncSession

async def get_bm_health_rows(session: AsyncSession, region_ids=None, master_store_ids=None):
    now = datetime.utcnow()
    stmt = select(
        BusinessManagerConfig.id.label("bm_id"),
        BusinessManagerConfig.name.label("bm_name"),
        BusinessManagerConfig.master_store_id,
        BusinessManagerConfig.last_successful_fetch_meta_at,
        BusinessManagerConfig.last_successful_fetch_shopify_at,
        BusinessManagerConfig.meta_token_status,
        BusinessManagerConfig.is_active,
        (
            func.coalesce(
                func.extract('epoch', now - BusinessManagerConfig.last_successful_fetch_meta_at), 86400
            ) / 3600
        ).label("age_meta_hours"),
        (
            func.coalesce(
                func.extract('epoch', now - BusinessManagerConfig.last_successful_fetch_shopify_at), 86400
            ) / 3600
        ).label("age_shopify_hours"),
    )

    if master_store_ids:
        stmt = stmt.filter(BusinessManagerConfig.master_store_id.in_(master_store_ids))
    if region_ids:
        stmt = stmt.join(MasterStoreConfig).filter(MasterStoreConfig.region_id.in_(region_ids))

    return (await session.execute(stmt)).all()