from typing import Any, Dict, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

async def paginate(session: AsyncSession, stmt: select, page: int, page_size: int) -> Tuple[List[Any], Dict[str, int]]:
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_items = (await session.execute(total_stmt)).scalar()
    items_stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = (await session.execute(items_stmt)).scalars().all()
    total_pages = (total_items + page_size - 1) // page_size
    return items, {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }