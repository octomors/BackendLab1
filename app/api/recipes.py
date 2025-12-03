from models import db_helper, Recipe, User
from schemas import RecipeCreate, RecipeUpdate, RecipeResponse
from repositories import RecipeRepository
from queries import RecipeQueries
from services import RecipeService
from authentication.fastapi_users import current_active_user
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page

router = APIRouter(
    tags=["Recipes"],
    prefix="/recipes",
)


# Create
@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: RecipeCreate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_user),
):
    repository = RecipeRepository(session)
    service = RecipeService(session)
    db_recipe = await repository.create(recipe, user.id)
    return await service.build_recipe_response(db_recipe)


# Read all
@router.get("/", response_model=List[RecipeResponse])
async def read_recipes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = RecipeQueries(session)
    service = RecipeService(session)
    recipes = await queries.get_all(skip, limit)

    response = []
    for recipe in recipes:
        recipe_response = await service.build_recipe_response(recipe)
        response.append(recipe_response)

    return response


# Read by ID
@router.get("/{recipe_id}", response_model=RecipeResponse)
async def read_recipe(
    recipe_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = RecipeQueries(session)
    service = RecipeService(session)
    recipe = await queries.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return await service.build_recipe_response(recipe)


# Update
@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe_update: RecipeUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_user),
):
    repository = RecipeRepository(session)
    service = RecipeService(session)
    
    db_recipe = await repository.get_by_id(recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if user is the author
    if db_recipe.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own recipes")

    updated_recipe = await repository.update(recipe_id, recipe_update)
    return await service.build_recipe_response(updated_recipe)


# Delete
@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_user),
):
    repository = RecipeRepository(session)
    
    db_recipe = await repository.get_by_id(recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if user is the author
    if db_recipe.author_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own recipes")
    
    await repository.delete(recipe_id)
    return


# Get all recipes with pagination, filtering, and sorting
@router.get("/paginated/", response_model=Page[RecipeResponse])
async def get_recipes_paginated(
    name__like: Optional[str] = Query(None, description="Search recipes by name (title)"),
    ingredient_id: Optional[List[int]] = Query(None, description="Filter by ingredient IDs"),
    sort: Optional[str] = Query("-id", description="Sort field (use '-' prefix for descending)"),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    service = RecipeService(session)
    return await service.get_paginated_recipes(name__like, ingredient_id, sort)
