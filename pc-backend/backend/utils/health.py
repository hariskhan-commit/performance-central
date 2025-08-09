from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.core import BusinessManagerConfig

async def compute_health_status(session: AsyncSession):
    stale_threshold = datetime.utcnow() - timedelta(hours=24)
    count_total = (await session.execute(select(func.count(BusinessManagerConfig.id)))).scalar()
    count_stale = (await session.execute(select(func.count(BusinessManagerConfig.id)).where(
        BusinessManagerConfig.last_successful_fetch_meta_at < stale_threshold
    ))).scalar()
    pct_stale = (count_stale / count_total) * 100 if count_total else 0
    if pct_stale < 5:
        return "Green"
    if pct_stale < 15:
        return "Amber"
    return "Red"

async def compute_freshness_score(session: AsyncSession):
    try:
        now = datetime.utcnow()
        stmt = select(func.percentile_cont(0.9).within_group(now - func.coalesce(BusinessManagerConfig.last_successful_fetch_meta_at, now)))
        if session.bind.dialect.name == 'postgresql':
            p90 = (await session.execute(stmt)).scalar()
            return int(100 - (p90.total_seconds() / 3600 / 24))
        else:
            return 0  # No percentile_cont in MySQL
    except:
        return 0