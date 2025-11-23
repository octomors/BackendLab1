from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Recipe, Cuisine, Allergen, RecipeAllergen, RecipeIngredient


async def build_recipe_response(recipe: Recipe, session: AsyncSession) -> dict:
    """
    Build a recipe response with nested cuisine, allergens, and ingredients data.

    Args:
        recipe: Recipe model instance
        session: AsyncSession for database queries

    Returns:
        Dictionary with recipe data including nested relationships
    """
    # Get cuisine
    cuisine = None
    if recipe.cuisine_id:
        cuisine_result = await session.execute(
            select(Cuisine).where(Cuisine.id == recipe.cuisine_id)
        )
        cuisine = cuisine_result.scalar_one_or_none()

    # Get allergens
    allergen_links_result = await session.execute(
        select(RecipeAllergen).where(RecipeAllergen.recipe_id == recipe.id)
    )
    allergen_links = allergen_links_result.scalars().all()
    allergen_ids = [link.allergen_id for link in allergen_links]

    allergens = []
    if allergen_ids:
        allergens_result = await session.execute(
            select(Allergen).where(Allergen.id.in_(allergen_ids))
        )
        allergens = allergens_result.scalars().all()

    # Get ingredients
    recipe_ingredients_result = await session.execute(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
    )
    recipe_ingredients = recipe_ingredients_result.scalars().all()

    ingredients = [
        {"id": ri.ingredient_id, "quantity": ri.quantity, "measurement": ri.measurement}
        for ri in recipe_ingredients
    ]

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "cooking_time": recipe.cooking_time,
        "difficulty": recipe.difficulty,
        "cuisine": {"id": cuisine.id, "name": cuisine.name} if cuisine else None,
        "allergens": [{"id": a.id, "name": a.name} for a in allergens],
        "ingredients": ingredients,
    }
