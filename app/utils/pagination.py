from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


async def paginate(
    db: AsyncSession,
    query,
    page: int = 1,
    page_size: int = 10
) -> tuple:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    paginated_query = query.limit(page_size).offset(offset)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return items, total, total_pages
