"""
Pytest configuration and fixtures for RecipeService testing.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from models.base import Base
from models.recipe import Recipe
from models.cuisine import Cuisine
from models.allergen import Allergen
from models.ingredient import Ingredient
from models.recipe_allergen import RecipeAllergen
from models.recipe_ingredient import RecipeIngredient
from models.users import User


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use uvloop if available, otherwise default."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create async session for testing."""
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def sample_user(session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_cuisine(session: AsyncSession) -> Cuisine:
    """Create a sample cuisine for testing."""
    cuisine = Cuisine(id=1, name="Italian")
    session.add(cuisine)
    await session.commit()
    await session.refresh(cuisine)
    return cuisine


@pytest_asyncio.fixture
async def sample_allergens(session: AsyncSession) -> list[Allergen]:
    """Create sample allergens for testing."""
    allergens = [
        Allergen(id=1, name="Gluten"),
        Allergen(id=2, name="Dairy"),
        Allergen(id=3, name="Nuts"),
    ]
    for allergen in allergens:
        session.add(allergen)
    await session.commit()
    for allergen in allergens:
        await session.refresh(allergen)
    return allergens


@pytest_asyncio.fixture
async def sample_ingredients(session: AsyncSession) -> list[Ingredient]:
    """Create sample ingredients for testing."""
    ingredients = [
        Ingredient(id=1, name="Pasta"),
        Ingredient(id=2, name="Tomato"),
        Ingredient(id=3, name="Cheese"),
        Ingredient(id=4, name="Olive Oil"),
    ]
    for ingredient in ingredients:
        session.add(ingredient)
    await session.commit()
    for ingredient in ingredients:
        await session.refresh(ingredient)
    return ingredients


@pytest_asyncio.fixture
async def sample_recipe(
    session: AsyncSession,
    sample_user: User,
    sample_cuisine: Cuisine,
    sample_allergens: list[Allergen],
    sample_ingredients: list[Ingredient],
) -> Recipe:
    """Create a sample recipe with all related entities for testing."""
    recipe = Recipe(
        id=1,
        title="Spaghetti Carbonara",
        description="Classic Italian pasta dish",
        cooking_time=30,
        difficulty=2,
        cuisine_id=sample_cuisine.id,
        author_id=sample_user.id,
    )
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    
    # Add allergens to recipe
    recipe_allergen1 = RecipeAllergen(recipe_id=recipe.id, allergen_id=sample_allergens[0].id)
    recipe_allergen2 = RecipeAllergen(recipe_id=recipe.id, allergen_id=sample_allergens[1].id)
    session.add(recipe_allergen1)
    session.add(recipe_allergen2)
    
    # Add ingredients to recipe
    recipe_ingredient1 = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=sample_ingredients[0].id,
        quantity=200.0,
        measurement=1,  # GRAMS
    )
    recipe_ingredient2 = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=sample_ingredients[2].id,
        quantity=100.0,
        measurement=1,  # GRAMS
    )
    session.add(recipe_ingredient1)
    session.add(recipe_ingredient2)
    
    await session.commit()
    await session.refresh(recipe)
    
    return recipe


@pytest_asyncio.fixture
async def multiple_recipes(
    session: AsyncSession,
    sample_user: User,
    sample_cuisine: Cuisine,
    sample_ingredients: list[Ingredient],
) -> list[Recipe]:
    """Create multiple recipes for pagination and filtering tests."""
    recipes = [
        Recipe(
            id=1,
            title="Spaghetti Carbonara",
            description="Classic Italian pasta dish",
            cooking_time=30,
            difficulty=2,
            cuisine_id=sample_cuisine.id,
            author_id=sample_user.id,
        ),
        Recipe(
            id=2,
            title="Margherita Pizza",
            description="Traditional Italian pizza",
            cooking_time=45,
            difficulty=3,
            cuisine_id=sample_cuisine.id,
            author_id=sample_user.id,
        ),
        Recipe(
            id=3,
            title="Caesar Salad",
            description="Fresh salad with Caesar dressing",
            cooking_time=15,
            difficulty=1,
            cuisine_id=None,  # No cuisine
            author_id=sample_user.id,
        ),
    ]
    
    for recipe in recipes:
        session.add(recipe)
    await session.commit()
    
    # Add ingredients to first recipe
    ri1 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=sample_ingredients[0].id,  # Pasta
        quantity=200.0,
        measurement=1,
    )
    ri2 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=sample_ingredients[2].id,  # Cheese
        quantity=100.0,
        measurement=1,
    )
    session.add(ri1)
    session.add(ri2)
    
    # Add ingredients to second recipe
    ri3 = RecipeIngredient(
        recipe_id=2,
        ingredient_id=sample_ingredients[1].id,  # Tomato
        quantity=150.0,
        measurement=1,
    )
    ri4 = RecipeIngredient(
        recipe_id=2,
        ingredient_id=sample_ingredients[2].id,  # Cheese
        quantity=200.0,
        measurement=1,
    )
    session.add(ri3)
    session.add(ri4)
    
    # Add ingredient to third recipe
    ri5 = RecipeIngredient(
        recipe_id=3,
        ingredient_id=sample_ingredients[3].id,  # Olive Oil
        quantity=50.0,
        measurement=3,  # MILLILITERS
    )
    session.add(ri5)
    
    await session.commit()
    
    for recipe in recipes:
        await session.refresh(recipe)
    
    return recipes
