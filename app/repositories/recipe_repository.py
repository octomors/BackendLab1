from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Recipe, RecipeAllergen, RecipeIngredient
from schemas import RecipeCreate, RecipeUpdate


class RecipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recipe_data: RecipeCreate, author_id: int) -> Recipe:
        recipe_dict = recipe_data.model_dump(exclude={"allergen_ids", "ingredients"})
        recipe_dict["author_id"] = author_id
        db_recipe = Recipe(**recipe_dict)
        self.session.add(db_recipe)

        await self.session.flush()

        for allergen_id in recipe_data.allergen_ids:
            recipe_allergen = RecipeAllergen(
                recipe_id=db_recipe.id, allergen_id=allergen_id
            )
            self.session.add(recipe_allergen)

        for ingredient_input in recipe_data.ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=db_recipe.id,
                ingredient_id=ingredient_input.ingredient_id,
                quantity=ingredient_input.quantity,
                measurement=ingredient_input.measurement,
            )
            self.session.add(recipe_ingredient)

        await self.session.commit()
        await self.session.refresh(db_recipe)
        return db_recipe

    async def update(self, recipe_id: int, recipe_update: RecipeUpdate) -> Recipe | None:
        result = await self.session.execute(select(Recipe).where(Recipe.id == recipe_id))
        db_recipe = result.scalar_one_or_none()
        if not db_recipe:
            return None

        update_data = recipe_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_recipe, key, value)

        await self.session.commit()
        await self.session.refresh(db_recipe)
        return db_recipe

    async def delete(self, recipe_id: int) -> bool:
        result = await self.session.execute(select(Recipe).where(Recipe.id == recipe_id))
        db_recipe = result.scalar_one_or_none()
        if not db_recipe:
            return False

        await self.session.delete(db_recipe)
        await self.session.commit()
        return True

    async def get_by_id(self, recipe_id: int) -> Recipe | None:
        result = await self.session.execute(select(Recipe).where(Recipe.id == recipe_id))
        return result.scalar_one_or_none()
