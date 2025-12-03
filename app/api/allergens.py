from models import db_helper
from schemas import AllergenCreate, AllergenUpdate, AllergenResponse
from repositories import AllergenRepository
from queries import AllergenQueries
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Allergens"],
    prefix="/allergens",
)


# Create Allergen
@router.post("/", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED)
async def create_allergen(
    allergen: AllergenCreate, session: AsyncSession = Depends(db_helper.session_getter)
):
    repository = AllergenRepository(session)
    return await repository.create(allergen)


# Read all Allergens
@router.get("/", response_model=List[AllergenResponse])
async def read_allergens(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = AllergenQueries(session)
    return await queries.get_all(skip, limit)


# Read Allergen by ID
@router.get("/{allergen_id}", response_model=AllergenResponse)
async def read_allergen(
    allergen_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = AllergenQueries(session)
    allergen = await queries.get_by_id(allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return allergen


# Update Allergen
@router.put("/{allergen_id}", response_model=AllergenResponse)
async def update_allergen(
    allergen_id: int,
    allergen_update: AllergenUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    queries = AllergenQueries(session)
    allergen = await queries.get_by_id(allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    
    repository = AllergenRepository(session)
    return await repository.update(allergen_id, allergen_update)


# Delete Allergen
@router.delete("/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergen(
    allergen_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    queries = AllergenQueries(session)
    allergen = await queries.get_by_id(allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    
    repository = AllergenRepository(session)
    await repository.delete(allergen_id)
    return
