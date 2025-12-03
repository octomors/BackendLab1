from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from models import Recipe, Cuisine, Allergen, RecipeAllergen, RecipeIngredient, Ingredient, User
from queries import RecipeQueries, IngredientQueries
from schemas import RecipeResponse
from fastapi_pagination.ext.sqlalchemy import paginate as apaginate


class RecipeService:
    """
    Service class containing business logic for recipe operations.
    This class can be tested independently of the endpoints.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.recipe_queries = RecipeQueries(session)
        self.ingredient_queries = IngredientQueries(session)

    async def get_paginated_recipes(
        self,
        name__like: Optional[str] = None,
        ingredient_id: Optional[List[int]] = None,
        sort: Optional[str] = "-id",
    ):
        """
        Get recipes with pagination, filtering, and sorting.
        
        Args:
            name__like: Search recipes by name (title)
            ingredient_id: Filter by ingredient IDs
            sort: Sort field (use '-' prefix for descending)
        
        Returns:
            Paginated result with recipe responses
        """
        query = self.recipe_queries.build_base_query()

        # Apply text search filter
        if name__like:
            query = self.recipe_queries.apply_name_filter(query, name__like)

        # Apply ingredient filter
        if ingredient_id:
            recipe_ids = await self.recipe_queries.get_recipe_ids_by_ingredient_ids(ingredient_id)
            query = self.recipe_queries.apply_recipe_ids_filter(query, recipe_ids)

        # Apply sorting
        if sort:
            query = self.recipe_queries.apply_sorting(query, sort)

        # Build transformer for pagination
        async def transformer(items):
            recipes_with_details = []
            for recipe in items:
                recipe_response = await self.build_recipe_response(recipe)
                recipes_with_details.append(RecipeResponse(**recipe_response))
            return recipes_with_details

        paginated_result = await apaginate(self.session, query, transformer=transformer)
        return paginated_result

    async def get_recipes_by_ingredient(
        self,
        ingredient_id: int,
        include: Optional[str] = None,
        select_fields: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get recipes that contain a specific ingredient.
        
        Args:
            ingredient_id: The ingredient ID to filter by
            include: Comma-separated list of related entities to include
            select_fields: Comma-separated list of fields to return
        
        Returns:
            List of recipe dictionaries
        
        Raises:
            ValueError: If ingredient not found
        """
        # Check if ingredient exists
        ingredient = await self.ingredient_queries.get_by_id(ingredient_id)
        if not ingredient:
            raise ValueError("Ingredient not found")

        # Get recipe IDs that use this ingredient
        recipe_ids = await self.ingredient_queries.get_recipe_ids_by_ingredient(ingredient_id)

        if not recipe_ids:
            return []

        # Get recipes
        recipes = await self.recipe_queries.get_by_ids(recipe_ids)

        # Parse include parameter
        includes = []
        if include:
            includes = [i.strip() for i in include.split(",")]

        # Parse select parameter
        selected_fields = []
        if select_fields:
            selected_fields = [f.strip() for f in select_fields.split(",")]

        # Build response
        response = []
        for recipe in recipes:
            if includes:
                recipe_dict = await self.build_recipe_response_selective(recipe, includes)
            else:
                recipe_dict = {
                    "id": recipe.id,
                    "title": recipe.title,
                    "difficulty": recipe.difficulty,
                    "description": recipe.description,
                    "cooking_time": recipe.cooking_time,
                }

            # Apply field selection
            if selected_fields:
                recipe_dict = {k: v for k, v in recipe_dict.items() if k in selected_fields}

            response.append(recipe_dict)

        return response

    async def build_recipe_response(self, recipe: Recipe) -> dict:
        """
        Build response body for recipe with nested cuisine, allergens and ingredients.
        """
        cuisine = None
        if recipe.cuisine_id:
            cuisine_result = await self.session.execute(
                select(Cuisine).where(Cuisine.id == recipe.cuisine_id)
            )
            cuisine = cuisine_result.scalar_one_or_none()

        # Get author information
        author_result = await self.session.execute(
            select(User).where(User.id == recipe.author_id)
        )
        author = author_result.scalar_one_or_none()

        allergen_links_result = await self.session.execute(
            select(RecipeAllergen).where(RecipeAllergen.recipe_id == recipe.id)
        )
        allergen_links = allergen_links_result.scalars().all()
        allergen_ids = [link.allergen_id for link in allergen_links]

        allergens = []
        if allergen_ids:
            allergens_result = await self.session.execute(
                select(Allergen).where(Allergen.id.in_(allergen_ids))
            )
            allergens = allergens_result.scalars().all()

        recipe_ingredients_result = await self.session.execute(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
        )
        recipe_ingredients = recipe_ingredients_result.scalars().all()

        ingredient_ids = [ri.ingredient_id for ri in recipe_ingredients]
        ingredients_dict = {}
        if ingredient_ids:
            ingredients_result = await self.session.execute(
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
            "author": {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
            } if author else None,
            "allergens": [{"id": a.id, "name": a.name} for a in allergens],
            "ingredients": ingredients,
        }

    async def build_recipe_response_selective(self, recipe: Recipe, includes: List[str]) -> dict:
        """
        Build response body for recipe with selective nested entities.
        """
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
                cuisine_result = await self.session.execute(
                    select(Cuisine).where(Cuisine.id == recipe.cuisine_id)
                )
                cuisine = cuisine_result.scalar_one_or_none()
            recipe_dict["cuisine"] = {"id": cuisine.id, "name": cuisine.name} if cuisine else None

        if "author" in includes:
            author_result = await self.session.execute(
                select(User).where(User.id == recipe.author_id)
            )
            author = author_result.scalar_one_or_none()
            recipe_dict["author"] = {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
            } if author else None

        if "allergens" in includes:
            allergen_links_result = await self.session.execute(
                select(RecipeAllergen).where(RecipeAllergen.recipe_id == recipe.id)
            )
            allergen_links = allergen_links_result.scalars().all()
            allergen_ids = [link.allergen_id for link in allergen_links]

            allergens = []
            if allergen_ids:
                allergens_result = await self.session.execute(
                    select(Allergen).where(Allergen.id.in_(allergen_ids))
                )
                allergens = allergens_result.scalars().all()

            recipe_dict["allergens"] = [{"id": a.id, "name": a.name} for a in allergens]

        if "ingredients" in includes:
            recipe_ingredients_result = await self.session.execute(
                select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
            )
            recipe_ingredients = recipe_ingredients_result.scalars().all()

            ingredient_ids = [ri.ingredient_id for ri in recipe_ingredients]
            ingredients_dict = {}
            if ingredient_ids:
                ingredients_result = await self.session.execute(
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
