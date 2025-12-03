from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Ingredient, RecipeIngredient
from typing import List, Optional


class IngredientQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Ingredient]:
        result = await self.session.execute(select(Ingredient).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        result = await self.session.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        return result.scalar_one_or_none()

    async def get_recipe_ids_by_ingredient(self, ingredient_id: int) -> List[int]:
        result = await self.session.execute(
            select(RecipeIngredient).where(RecipeIngredient.ingredient_id == ingredient_id)
        )
        recipe_ingredients = result.scalars().all()
        return [ri.recipe_id for ri in recipe_ingredients]
