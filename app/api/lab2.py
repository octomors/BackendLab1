from models import (
    db_helper,
    Cuisine,
    Allergen,
    Ingredient,
    Recipe,
    RecipeAllergen,
    RecipeIngredient,
    MeasurementEnum,
)
from schemas import (
    CuisineCreate,
    CuisineUpdate,
    CuisineResponse,
    AllergenCreate,
    AllergenUpdate,
    AllergenResponse,
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse,
    RecipeCreate,
    RecipeResponse,
)
from fastapi import APIRouter, HTTPException, status, Depends
from config import settings
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(
    tags=["Lab2"],
    prefix="/lab2",
)

# ============================================================================
# CUISINE CRUD
# ============================================================================


# Create Cuisine
@router.post(
    "/cuisines/", response_model=CuisineResponse, status_code=status.HTTP_201_CREATED
)
async def create_cuisine(
    cuisine: CuisineCreate, session: AsyncSession = Depends(db_helper.session_getter)
):
    db_cuisine = Cuisine(**cuisine.model_dump())
    session.add(db_cuisine)
    await session.commit()
    await session.refresh(db_cuisine)
    return db_cuisine


# Read all Cuisines
@router.get("/cuisines/", response_model=List[CuisineResponse])
async def read_cuisines(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Cuisine).offset(skip).limit(limit))
    return result.scalars().all()


# Read Cuisine by ID
@router.get("/cuisines/{cuisine_id}", response_model=CuisineResponse)
async def read_cuisine(
    cuisine_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
    cuisine = result.scalar_one_or_none()
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine


# Update Cuisine
@router.put("/cuisines/{cuisine_id}", response_model=CuisineResponse)
async def update_cuisine(
    cuisine_id: int,
    cuisine_update: CuisineUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
    db_cuisine = result.scalar_one_or_none()
    if not db_cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")

    update_data = cuisine_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cuisine, key, value)

    await session.commit()
    await session.refresh(db_cuisine)
    return db_cuisine


# Delete Cuisine
@router.delete("/cuisines/{cuisine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cuisine(
    cuisine_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Cuisine).where(Cuisine.id == cuisine_id))
    db_cuisine = result.scalar_one_or_none()
    if not db_cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    await session.delete(db_cuisine)
    await session.commit()
    return


# ============================================================================
# ALLERGEN CRUD
# ============================================================================


# Create Allergen
@router.post(
    "/allergens/", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED
)
async def create_allergen(
    allergen: AllergenCreate, session: AsyncSession = Depends(db_helper.session_getter)
):
    db_allergen = Allergen(**allergen.model_dump())
    session.add(db_allergen)
    await session.commit()
    await session.refresh(db_allergen)
    return db_allergen


# Read all Allergens
@router.get("/allergens/", response_model=List[AllergenResponse])
async def read_allergens(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Allergen).offset(skip).limit(limit))
    return result.scalars().all()


# Read Allergen by ID
@router.get("/allergens/{allergen_id}", response_model=AllergenResponse)
async def read_allergen(
    allergen_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Allergen).where(Allergen.id == allergen_id))
    allergen = result.scalar_one_or_none()
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return allergen


# Update Allergen
@router.put("/allergens/{allergen_id}", response_model=AllergenResponse)
async def update_allergen(
    allergen_id: int,
    allergen_update: AllergenUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Allergen).where(Allergen.id == allergen_id))
    db_allergen = result.scalar_one_or_none()
    if not db_allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")

    update_data = allergen_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_allergen, key, value)

    await session.commit()
    await session.refresh(db_allergen)
    return db_allergen


# Delete Allergen
@router.delete("/allergens/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergen(
    allergen_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Allergen).where(Allergen.id == allergen_id))
    db_allergen = result.scalar_one_or_none()
    if not db_allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    await session.delete(db_allergen)
    await session.commit()
    return


# ============================================================================
# INGREDIENT CRUD
# ============================================================================


# Create Ingredient
@router.post(
    "/ingredients/",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(
    ingredient: IngredientCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    db_ingredient = Ingredient(**ingredient.model_dump())
    session.add(db_ingredient)
    await session.commit()
    await session.refresh(db_ingredient)
    return db_ingredient


# Read all Ingredients
@router.get("/ingredients/", response_model=List[IngredientResponse])
async def read_ingredients(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(select(Ingredient).offset(skip).limit(limit))
    return result.scalars().all()


# Read Ingredient by ID
@router.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
async def read_ingredient(
    ingredient_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )
    ingredient = result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


# Update Ingredient
@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
    ingredient_id: int,
    ingredient_update: IngredientUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await session.execute(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )
    db_ingredient = result.scalar_one_or_none()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    update_data = ingredient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)

    await session.commit()
    await session.refresh(db_ingredient)
    return db_ingredient


# Delete Ingredient
@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )
    db_ingredient = result.scalar_one_or_none()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    await session.delete(db_ingredient)
    await session.commit()
    return


# ============================================================================
# TASK D: Get recipes by ingredient
# ============================================================================


@router.get("/ingredients/{ingredient_id}/recipes", response_model=List[RecipeResponse])
async def get_recipes_by_ingredient(
    ingredient_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    # First check if ingredient exists
    ingredient_result = await session.execute(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    )
    ingredient = ingredient_result.scalar_one_or_none()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Get all recipe_ids that use this ingredient
    recipe_ingredients_result = await session.execute(
        select(RecipeIngredient).where(RecipeIngredient.ingredient_id == ingredient_id)
    )
    recipe_ingredients = recipe_ingredients_result.scalars().all()

    recipe_ids = [ri.recipe_id for ri in recipe_ingredients]

    if not recipe_ids:
        return []

    # Get all recipes with these IDs
    recipes_result = await session.execute(
        select(Recipe).where(Recipe.id.in_(recipe_ids))
    )
    recipes = recipes_result.scalars().all()

    # Build response with nested data
    response = []
    for recipe in recipes:
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
        recipe_ingredients_for_recipe_result = await session.execute(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
        )
        recipe_ingredients_for_recipe = (
            recipe_ingredients_for_recipe_result.scalars().all()
        )

        ingredients = [
            {
                "id": ri.ingredient_id,
                "quantity": ri.quantity,
                "measurement": ri.measurement,
            }
            for ri in recipe_ingredients_for_recipe
        ]

        recipe_response = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "cooking_time": recipe.cooking_time,
            "difficulty": recipe.difficulty,
            "cuisine": {"id": cuisine.id, "name": cuisine.name} if cuisine else None,
            "allergens": [{"id": a.id, "name": a.name} for a in allergens],
            "ingredients": ingredients,
        }

        response.append(recipe_response)

    return response
