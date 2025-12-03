from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Ingredient
from schemas import IngredientCreate, IngredientUpdate


class IngredientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ingredient_data: IngredientCreate) -> Ingredient:
        db_ingredient = Ingredient(**ingredient_data.model_dump())
        self.session.add(db_ingredient)
        await self.session.commit()
        await self.session.refresh(db_ingredient)
        return db_ingredient

    async def update(self, ingredient_id: int, ingredient_update: IngredientUpdate) -> Ingredient | None:
        result = await self.session.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        db_ingredient = result.scalar_one_or_none()
        if not db_ingredient:
            return None

        update_data = ingredient_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ingredient, key, value)

        await self.session.commit()
        await self.session.refresh(db_ingredient)
        return db_ingredient

    async def delete(self, ingredient_id: int) -> bool:
        result = await self.session.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        db_ingredient = result.scalar_one_or_none()
        if not db_ingredient:
            return False

        await self.session.delete(db_ingredient)
        await self.session.commit()
        return True
