from models import db_helper
from schemas import IngredientCreate, IngredientUpdate, IngredientResponse
from repositories import IngredientRepository
from queries import IngredientQueries
from services import RecipeService
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Ingredients"],
    prefix="/ingredients",
)


# Create Ingredient
@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    ingredient: IngredientCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    repository = IngredientRepository(session)
    return await repository.create(ingredient)


# Read all Ingredients
@router.get("/", response_model=List[IngredientResponse])
async def read_ingredients(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = IngredientQueries(session)
    return await queries.get_all(skip, limit)


# Read Ingredient by ID
@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def read_ingredient(
    ingredient_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = IngredientQueries(session)
    ingredient = await queries.get_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


# Update Ingredient
@router.put("/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
    ingredient_id: int,
    ingredient_update: IngredientUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = IngredientQueries(session)
    ingredient = await queries.get_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    repository = IngredientRepository(session)
    return await repository.update(ingredient_id, ingredient_update)


# Delete Ingredient
@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = IngredientQueries(session)
    ingredient = await queries.get_by_id(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    repository = IngredientRepository(session)
    await repository.delete(ingredient_id)
    return


# Get recipes by ingredient
@router.get("/{ingredient_id}/recipes")
async def get_recipes_by_ingredient(
    ingredient_id: int,
    include: Optional[str] = Query(None, description="Comma-separated list of related entities to include: cuisine, ingredients, allergens, author"),
    select: Optional[str] = Query(None, description="Comma-separated list of fields to return: id, title, difficulty, description, cooking_time"),
    session: AsyncSession = Depends(db_helper.session_getter)
):
    service = RecipeService(session)
    try:
        return await service.get_recipes_by_ingredient(ingredient_id, include, select)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
