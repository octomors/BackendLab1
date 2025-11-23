from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Recipe, Cuisine, Allergen, RecipeAllergen, RecipeIngredient
from typing import List


async def build_recipe_response_selective(recipe: Recipe, session: AsyncSession, includes: List[str]) -> dict:
    """
    Cтроит response body для рецепта с вложенной кухней, аллергенами и ингридиентами c возможностью выбора параметров
    """
    # Start with basic recipe fields
    recipe_dict = {
        "id": recipe.id,
        "title": recipe.title,
        "difficulty": recipe.difficulty,
        "description": recipe.description,
        "cooking_time": recipe.cooking_time,
    }
    
    if "cuisine" in includes:
        cuisine = None
        if recipe.cuisine_id:
            cuisine_result = await session.execute(
                select(Cuisine).where(Cuisine.id == recipe.cuisine_id)
            )
            cuisine = cuisine_result.scalar_one_or_none()
        recipe_dict["cuisine"] = {"id": cuisine.id, "name": cuisine.name} if cuisine else None
    
    if "allergens" in includes:
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
        
        recipe_dict["allergens"] = [{"id": a.id, "name": a.name} for a in allergens]
    
    if "ingredients" in includes:
        recipe_ingredients_result = await session.execute(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
        )
        recipe_ingredients = recipe_ingredients_result.scalars().all()
        
        ingredient_ids = [ri.ingredient_id for ri in recipe_ingredients]
        ingredients_dict = {}
        if ingredient_ids:
            from models import Ingredient
            
            ingredients_result = await session.execute(
                select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
            )
            ingredients_list = ingredients_result.scalars().all()
            ingredients_dict = {ing.id: ing.name for ing in ingredients_list}
        
        ingredients = [
            {
                "id": ri.ingredient_id,
                "name": ingredients_dict.get(ri.ingredient_id, ""),
                "quantity": ri.quantity,
                "measurement": ri.measurement,
            }
            for ri in recipe_ingredients
        ]
        recipe_dict["ingredients"] = ingredients
    
    return recipe_dict


async def build_recipe_response(recipe: Recipe, session: AsyncSession) -> dict:
    """
    Cтроит response body для рецепта с вложенной кухней, аллергенами и ингридиентами
    """

    cuisine = None
    if recipe.cuisine_id:
        cuisine_result = await session.execute(
            select(Cuisine).where(Cuisine.id == recipe.cuisine_id)
        )
        cuisine = cuisine_result.scalar_one_or_none()

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

    recipe_ingredients_result = await session.execute(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
    )
    recipe_ingredients = recipe_ingredients_result.scalars().all()

    ingredient_ids = [ri.ingredient_id for ri in recipe_ingredients]
    ingredients_dict = {}
    if ingredient_ids:
        from models import Ingredient

        ingredients_result = await session.execute(
            select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        )
        ingredients_list = ingredients_result.scalars().all()
        ingredients_dict = {ing.id: ing.name for ing in ingredients_list}

    ingredients = [
        {
            "id": ri.ingredient_id,
            "name": ingredients_dict.get(ri.ingredient_id, ""),
            "quantity": ri.quantity,
            "measurement": ri.measurement,
        }
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
