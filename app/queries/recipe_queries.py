from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Recipe, RecipeIngredient
from typing import List, Optional


class RecipeQueries:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Recipe]:
        result = await self.session.execute(select(Recipe).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        result = await self.session.execute(select(Recipe).where(Recipe.id == recipe_id))
        return result.scalar_one_or_none()

    async def get_recipe_ids_by_ingredient_ids(self, ingredient_ids: List[int]) -> List[int]:
        result = await self.session.execute(
            select(RecipeIngredient.recipe_id)
            .where(RecipeIngredient.ingredient_id.in_(ingredient_ids))
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def get_by_ids(self, recipe_ids: List[int]) -> List[Recipe]:
        result = await self.session.execute(
            select(Recipe).where(Recipe.id.in_(recipe_ids))
        )
        return list(result.scalars().all())

    def build_base_query(self):
        return select(Recipe)

    def apply_name_filter(self, query, name_like: str):
        return query.where(Recipe.title.ilike(f"%{name_like}%"))

    def apply_recipe_ids_filter(self, query, recipe_ids: List[int]):
        if not recipe_ids:
            return query.where(Recipe.id.in_([-1]))  # No match condition
        return query.where(Recipe.id.in_(recipe_ids))

    def apply_sorting(self, query, sort: str):
        if sort.startswith("-"):
            field_name = sort[1:]
            if hasattr(Recipe, field_name):
                return query.order_by(getattr(Recipe, field_name).desc())
        else:
            if hasattr(Recipe, sort):
                return query.order_by(getattr(Recipe, sort))
        return query
