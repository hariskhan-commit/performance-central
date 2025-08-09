from typing import List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from backend.utils.fx import get_rate

async def bulk_convert(
    session: AsyncSession,
    rows: List[Dict[str, Any]],
    fields: Tuple[str, ...],
    date_field: str = "date",
    currency_field: str = "currency_code"
):
    for row in rows:
        if row.get(currency_field) == "USD":
            continue
        rate = await get_rate(session, row[date_field], row[currency_field])
        for field in fields:
            if field in row:
                row[field] = row[field] * rate if row[field] is not None else Decimal(0)