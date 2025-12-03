from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Allergen
from schemas import AllergenCreate, AllergenUpdate


class AllergenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, allergen_data: AllergenCreate) -> Allergen:
        db_allergen = Allergen(**allergen_data.model_dump())
        self.session.add(db_allergen)
        await self.session.commit()
        await self.session.refresh(db_allergen)
        return db_allergen

    async def update(self, allergen_id: int, allergen_update: AllergenUpdate) -> Allergen | None:
        result = await self.session.execute(select(Allergen).where(Allergen.id == allergen_id))
        db_allergen = result.scalar_one_or_none()
        if not db_allergen:
            return None

        update_data = allergen_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_allergen, key, value)

        await self.session.commit()
        await self.session.refresh(db_allergen)
        return db_allergen

    async def delete(self, allergen_id: int) -> bool:
        result = await self.session.execute(select(Allergen).where(Allergen.id == allergen_id))
        db_allergen = result.scalar_one_or_none()
        if not db_allergen:
            return False

        await self.session.delete(db_allergen)
        await self.session.commit()
        return True
