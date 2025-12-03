"""
Tests for RecipeService class.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.recipe_service import RecipeService
from models.recipe import Recipe
from models.cuisine import Cuisine
from models.allergen import Allergen
from models.ingredient import Ingredient
from models.users import User


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
