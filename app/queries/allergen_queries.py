from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Allergen
from typing import List, Optional


class AllergenQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Allergen]:
        result = await self.session.execute(select(Allergen).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, allergen_id: int) -> Optional[Allergen]:
        result = await self.session.execute(select(Allergen).where(Allergen.id == allergen_id))
        return result.scalar_one_or_none()
