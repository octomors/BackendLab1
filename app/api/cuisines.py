from models import db_helper
from schemas import CuisineCreate, CuisineUpdate, CuisineResponse
from repositories import CuisineRepository
from queries import CuisineQueries
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Cuisines"],
    prefix="/cuisines",
)


# Create Cuisine
@router.post("/", response_model=CuisineResponse, status_code=status.HTTP_201_CREATED)
async def create_cuisine(
    cuisine: CuisineCreate, session: AsyncSession = Depends(db_helper.session_getter)
):
    repository = CuisineRepository(session)
    return await repository.create(cuisine)


# Read all Cuisines
@router.get("/", response_model=List[CuisineResponse])
async def read_cuisines(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = CuisineQueries(session)
    return await queries.get_all(skip, limit)


# Read Cuisine by ID
@router.get("/{cuisine_id}", response_model=CuisineResponse)
async def read_cuisine(
    cuisine_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = CuisineQueries(session)
    cuisine = await queries.get_by_id(cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine


# Update Cuisine
@router.put("/{cuisine_id}", response_model=CuisineResponse)
async def update_cuisine(
    cuisine_id: int,
    cuisine_update: CuisineUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = CuisineQueries(session)
    cuisine = await queries.get_by_id(cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    
    repository = CuisineRepository(session)
    return await repository.update(cuisine_id, cuisine_update)


# Delete Cuisine
@router.delete("/{cuisine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cuisine(
    cuisine_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = CuisineQueries(session)
    cuisine = await queries.get_by_id(cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    
    repository = CuisineRepository(session)
    await repository.delete(cuisine_id)
    return
