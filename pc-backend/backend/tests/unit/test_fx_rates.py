import pytest
from decimal import Decimal
from datetime import date
from backend.models.aggregated import FXDailyRate
from backend.utils.fx import get_rate

@pytest.mark.asyncio
async def test_get_rate_prefers_manual(db_session):
    test_date = date.today()
    manual_rate = FXDailyRate(date=test_date, from_currency="EUR", to_currency="USD", rate=Decimal("1.50"), source="manual")
    auto_rate = FXDailyRate(date=test_date, from_currency="EUR", to_currency="USD", rate=Decimal("1.10"), source="exchangerate.host")
    db_session.add_all([manual_rate, auto_rate])
    await db_session.commit()
    rate = await get_rate(db_session, test_date, "EUR")
    assert rate == Decimal("1.50")

@pytest.mark.asyncio
async def test_get_rate_falls_back_to_auto(db_session):
    test_date = date.today()
    auto_rate = FXDailyRate(date=test_date, from_currency="EUR", to_currency="USD", rate=Decimal("1.10"), source="exchangerate.host")
    db_session.add(auto_rate)
    await db_session.commit()
    rate = await get_rate(db_session, test_date, "EUR")
    assert rate == Decimal("1.10")

@pytest.mark.asyncio
async def test_get_rate_defaults_to_one(db_session):
    test_date = date.today()
    rate = await get_rate(db_session, test_date, "EUR")
    assert rate == Decimal("1.0")