from decimal import Decimal
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.aggregated import FXDailyRate

async def get_rate(session: AsyncSession, day: date, from_ccy: str, to_ccy: str = "USD") -> Decimal:
    rate = (await session.execute(select(FXDailyRate.rate).filter_by(date=day, from_currency=from_ccy, to_currency=to_ccy, source="manual"))).scalar()
    if rate is None:
        rate = (await session.execute(select(FXDailyRate.rate).filter_by(date=day, from_currency=from_ccy, to_currency=to_ccy, source="exchangerate.host"))).scalar()
    if rate is None:
        last_rate_stmt = select(FXDailyRate.rate).filter(FXDailyRate.date < day, FXDailyRate.from_currency == from_ccy, FXDailyRate.to_currency == to_ccy).order_by(FXDailyRate.date.desc()).limit(1)
        rate = (await session.execute(last_rate_stmt)).scalar() or Decimal("1.0")
    return rate