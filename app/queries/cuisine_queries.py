from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Cuisine
from typing import List, Optional


class CuisineQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Cuisine]:
        result = await self.session.execute(select(Cuisine).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, cuisine_id: int) -> Optional[Cuisine]:
        result = await self.session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
        return result.scalar_one_or_none()
