"""
Tests for RecipeService class.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, Params
from fastapi_pagination.api import set_params, set_page
from fastapi_pagination.utils import disable_installed_extensions_check

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Disable extension check for testing
disable_installed_extensions_check()

from services.recipe_service import RecipeService
from models.recipe import Recipe
from models.cuisine import Cuisine
from models.allergen import Allergen
from models.ingredient import Ingredient
from models.users import User
from schemas.recipe import RecipeResponse


class TestBuildRecipeResponse:
    """Tests for build_recipe_response method."""
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_full(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
        sample_cuisine: Cuisine,
        sample_user: User,
        sample_allergens: list[Allergen],
        sample_ingredients: list[Ingredient],
    ):
        """Test building full recipe response with all related entities."""
        service = RecipeService(session)
        response = await service.build_recipe_response(sample_recipe)
        
        # Check basic fields
        assert response["id"] == sample_recipe.id
        assert response["title"] == sample_recipe.title
        assert response["description"] == sample_recipe.description
        assert response["cooking_time"] == sample_recipe.cooking_time
        assert response["difficulty"] == sample_recipe.difficulty
        
        # Check cuisine
        assert response["cuisine"] is not None
        assert response["cuisine"]["id"] == sample_cuisine.id
        assert response["cuisine"]["name"] == sample_cuisine.name
        
        # Check author
        assert response["author"] is not None
        assert response["author"]["id"] == sample_user.id
        assert response["author"]["first_name"] == sample_user.first_name
        assert response["author"]["last_name"] == sample_user.last_name
        
        # Check allergens
        assert len(response["allergens"]) == 2
        allergen_names = [a["name"] for a in response["allergens"]]
        assert "Gluten" in allergen_names
        assert "Dairy" in allergen_names
        
        # Check ingredients
        assert len(response["ingredients"]) == 2
        ingredient_names = [i["name"] for i in response["ingredients"]]
        assert "Pasta" in ingredient_names
        assert "Cheese" in ingredient_names
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_no_cuisine(
        self,
        session: AsyncSession,
        sample_user: User,
    ):
        """Test building recipe response when cuisine is None."""
        # Create recipe without cuisine
        recipe = Recipe(
            id=100,
            title="Simple Salad",
            description="A simple salad",
            cooking_time=10,
            difficulty=1,
            cuisine_id=None,
            author_id=sample_user.id,
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)
        
        service = RecipeService(session)
        response = await service.build_recipe_response(recipe)
        
        assert response["cuisine"] is None
        assert response["author"] is not None
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_no_allergens(
        self,
        session: AsyncSession,
        sample_user: User,
        sample_cuisine: Cuisine,
    ):
        """Test building recipe response when there are no allergens."""
        recipe = Recipe(
            id=101,
            title="Allergen Free Dish",
            description="No allergens",
            cooking_time=20,
            difficulty=1,
            cuisine_id=sample_cuisine.id,
            author_id=sample_user.id,
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)
        
        service = RecipeService(session)
        response = await service.build_recipe_response(recipe)
        
        assert response["allergens"] == []
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_no_ingredients(
        self,
        session: AsyncSession,
        sample_user: User,
        sample_cuisine: Cuisine,
    ):
        """Test building recipe response when there are no ingredients."""
        recipe = Recipe(
            id=102,
            title="No Ingredient Dish",
            description="No ingredients",
            cooking_time=5,
            difficulty=1,
            cuisine_id=sample_cuisine.id,
            author_id=sample_user.id,
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)
        
        service = RecipeService(session)
        response = await service.build_recipe_response(recipe)
        
        assert response["ingredients"] == []


class TestBuildRecipeResponseSelective:
    """Tests for build_recipe_response_selective method."""
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_base_fields(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
    ):
        """Test building recipe response with only base fields (empty includes)."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(sample_recipe, [])
        
        # Check basic fields are present
        assert response["id"] == sample_recipe.id
        assert response["title"] == sample_recipe.title
        assert response["description"] == sample_recipe.description
        assert response["cooking_time"] == sample_recipe.cooking_time
        assert response["difficulty"] == sample_recipe.difficulty
        
        # Check that optional fields are not included
        assert "cuisine" not in response
        assert "author" not in response
        assert "allergens" not in response
        assert "ingredients" not in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_cuisine_only(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
        sample_cuisine: Cuisine,
    ):
        """Test building recipe response with only cuisine included."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(sample_recipe, ["cuisine"])
        
        assert "cuisine" in response
        assert response["cuisine"]["id"] == sample_cuisine.id
        assert response["cuisine"]["name"] == sample_cuisine.name
        
        # Check that other optional fields are not included
        assert "author" not in response
        assert "allergens" not in response
        assert "ingredients" not in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_author_only(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
        sample_user: User,
    ):
        """Test building recipe response with only author included."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(sample_recipe, ["author"])
        
        assert "author" in response
        assert response["author"]["id"] == sample_user.id
        assert response["author"]["first_name"] == sample_user.first_name
        
        # Check that other optional fields are not included
        assert "cuisine" not in response
        assert "allergens" not in response
        assert "ingredients" not in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_allergens_only(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
    ):
        """Test building recipe response with only allergens included."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(sample_recipe, ["allergens"])
        
        assert "allergens" in response
        assert len(response["allergens"]) == 2
        
        # Check that other optional fields are not included
        assert "cuisine" not in response
        assert "author" not in response
        assert "ingredients" not in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_ingredients_only(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
    ):
        """Test building recipe response with only ingredients included."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(sample_recipe, ["ingredients"])
        
        assert "ingredients" in response
        assert len(response["ingredients"]) == 2
        
        # Check that other optional fields are not included
        assert "cuisine" not in response
        assert "author" not in response
        assert "allergens" not in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_multiple_includes(
        self,
        session: AsyncSession,
        sample_recipe: Recipe,
    ):
        """Test building recipe response with multiple includes."""
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(
            sample_recipe, 
            ["cuisine", "author", "allergens", "ingredients"]
        )
        
        # All optional fields should be present
        assert "cuisine" in response
        assert "author" in response
        assert "allergens" in response
        assert "ingredients" in response
    
    @pytest.mark.asyncio
    async def test_build_recipe_response_selective_no_cuisine(
        self,
        session: AsyncSession,
        sample_user: User,
    ):
        """Test building recipe response selective when cuisine is None."""
        recipe = Recipe(
            id=103,
            title="No Cuisine Recipe",
            description="Recipe without cuisine",
            cooking_time=15,
            difficulty=2,
            cuisine_id=None,
            author_id=sample_user.id,
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)
        
        service = RecipeService(session)
        response = await service.build_recipe_response_selective(recipe, ["cuisine"])
        
        assert response["cuisine"] is None


class TestGetRecipesByIngredient:
    """Tests for get_recipes_by_ingredient method."""
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_success(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient ID."""
        service = RecipeService(session)
        
        # Get recipes with Cheese (ingredient_id=3)
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id  # Cheese
        )
        
        assert len(recipes) == 2
        titles = [r["title"] for r in recipes]
        assert "Spaghetti Carbonara" in titles
        assert "Margherita Pizza" in titles
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_no_recipes(
        self,
        session: AsyncSession,
        sample_user: User,
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes when no recipe uses the ingredient."""
        # Create ingredient without any recipe
        ingredient = Ingredient(id=100, name="Unused Ingredient")
        session.add(ingredient)
        await session.commit()
        
        service = RecipeService(session)
        recipes = await service.get_recipes_by_ingredient(ingredient_id=100)
        
        assert recipes == []
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_not_found(
        self,
        session: AsyncSession,
    ):
        """Test getting recipes with non-existent ingredient raises ValueError."""
        service = RecipeService(session)
        
        with pytest.raises(ValueError, match="Ingredient not found"):
            await service.get_recipes_by_ingredient(ingredient_id=9999)
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_include_cuisine(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with cuisine included."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="cuisine"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "cuisine" in recipe
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_include_author(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with author included."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="author"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "author" in recipe
            assert "first_name" in recipe["author"]
            assert "last_name" in recipe["author"]
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_include_allergens(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with allergens included."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="allergens"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "allergens" in recipe
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_include_ingredients(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with ingredients included."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="ingredients"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "ingredients" in recipe
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_multiple_includes(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with multiple includes."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="cuisine,author,ingredients"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "cuisine" in recipe
            assert "author" in recipe
            assert "ingredients" in recipe
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_select_fields(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with field selection."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            select_fields="id,title"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "id" in recipe
            assert "title" in recipe
            assert "description" not in recipe
            assert "cooking_time" not in recipe
    
    @pytest.mark.asyncio
    async def test_get_recipes_by_ingredient_with_include_and_select(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting recipes by ingredient with both include and select_fields."""
        service = RecipeService(session)
        
        recipes = await service.get_recipes_by_ingredient(
            ingredient_id=sample_ingredients[2].id,  # Cheese
            include="cuisine",
            select_fields="id,title,cuisine"
        )
        
        assert len(recipes) == 2
        for recipe in recipes:
            assert "id" in recipe
            assert "title" in recipe
            assert "cuisine" in recipe
            assert "description" not in recipe


class TestGetPaginatedRecipes:
    """Tests for get_paginated_recipes method."""
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_no_filters(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test getting paginated recipes without any filters."""
        service = RecipeService(session)
        
        # Set up pagination context
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes()
        
        assert result.total == 3
        assert len(result.items) == 3
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_name(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test getting paginated recipes with name filter."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(name__like="Spaghetti")
        
        assert result.total == 1
        assert result.items[0].title == "Spaghetti Carbonara"
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_name_case_insensitive(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test that name filter is case insensitive."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(name__like="SPAGHETTI")
        
        assert result.total == 1
        assert result.items[0].title == "Spaghetti Carbonara"
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_name_no_match(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test getting paginated recipes with name filter that has no matches."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(name__like="Nonexistent Recipe")
        
        assert result.total == 0
        assert len(result.items) == 0
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_ingredient(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting paginated recipes filtered by ingredient."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            # Filter by Cheese (ingredient_id=3) - should return 2 recipes
            result = await service.get_paginated_recipes(
                ingredient_id=[sample_ingredients[2].id]
            )
        
        assert result.total == 2
        titles = [item.title for item in result.items]
        assert "Spaghetti Carbonara" in titles
        assert "Margherita Pizza" in titles
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_multiple_ingredients(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting paginated recipes filtered by multiple ingredients."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            # Filter by Pasta and Cheese - should return recipes with either
            result = await service.get_paginated_recipes(
                ingredient_id=[sample_ingredients[0].id, sample_ingredients[2].id]
            )
        
        assert result.total == 2
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_filter_by_nonexistent_ingredient(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test getting paginated recipes with non-existent ingredient filter."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(ingredient_id=[9999])
        
        assert result.total == 0
        assert len(result.items) == 0
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_sort_by_id_ascending(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test sorting recipes by ID ascending."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(sort="id")
        
        assert result.total == 3
        assert result.items[0].id < result.items[1].id < result.items[2].id
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_sort_by_id_descending(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test sorting recipes by ID descending."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(sort="-id")
        
        assert result.total == 3
        assert result.items[0].id > result.items[1].id > result.items[2].id
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_sort_by_title(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test sorting recipes by title."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(sort="title")
        
        assert result.total == 3
        # Caesar Salad < Margherita Pizza < Spaghetti Carbonara
        assert result.items[0].title == "Caesar Salad"
        assert result.items[1].title == "Margherita Pizza"
        assert result.items[2].title == "Spaghetti Carbonara"
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_sort_by_cooking_time(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test sorting recipes by cooking time."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes(sort="cooking_time")
        
        assert result.total == 3
        # Caesar Salad (15) < Spaghetti Carbonara (30) < Margherita Pizza (45)
        assert result.items[0].cooking_time <= result.items[1].cooking_time
        assert result.items[1].cooking_time <= result.items[2].cooking_time
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_combined_filters(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
        sample_ingredients: list[Ingredient],
    ):
        """Test getting paginated recipes with combined name and ingredient filters."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            # Filter by name containing "Pizza" and ingredient Cheese
            result = await service.get_paginated_recipes(
                name__like="Pizza",
                ingredient_id=[sample_ingredients[2].id]  # Cheese
            )
        
        assert result.total == 1
        assert result.items[0].title == "Margherita Pizza"
    
    @pytest.mark.asyncio
    async def test_get_paginated_recipes_response_includes_all_fields(
        self,
        session: AsyncSession,
        multiple_recipes: list[Recipe],
    ):
        """Test that paginated response includes all expected fields."""
        service = RecipeService(session)
        
        with set_page(Page[RecipeResponse]), set_params(Params(page=1, size=50)):
            result = await service.get_paginated_recipes()
        
        # Check that response items have all expected fields
        item = result.items[0]
        assert hasattr(item, 'id')
        assert hasattr(item, 'title')
        assert hasattr(item, 'description')
        assert hasattr(item, 'cooking_time')
        assert hasattr(item, 'difficulty')
        assert hasattr(item, 'cuisine')
        assert hasattr(item, 'author')
        assert hasattr(item, 'allergens')
        assert hasattr(item, 'ingredients')
