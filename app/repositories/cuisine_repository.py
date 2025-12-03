from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Cuisine
from schemas import CuisineCreate, CuisineUpdate


class CuisineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, cuisine_data: CuisineCreate) -> Cuisine:
        db_cuisine = Cuisine(**cuisine_data.model_dump())
        self.session.add(db_cuisine)
        await self.session.commit()
        await self.session.refresh(db_cuisine)
        return db_cuisine

    async def update(self, cuisine_id: int, cuisine_update: CuisineUpdate) -> Cuisine | None:
        result = await self.session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
        db_cuisine = result.scalar_one_or_none()
        if not db_cuisine:
            return None

        update_data = cuisine_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_cuisine, key, value)

        await self.session.commit()
        await self.session.refresh(db_cuisine)
        return db_cuisine

    async def delete(self, cuisine_id: int) -> bool:
        result = await self.session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
        db_cuisine = result.scalar_one_or_none()
        if not db_cuisine:
            return False

        await self.session.delete(db_cuisine)
        await self.session.commit()
        return True
