from models import db_helper, Recipe, Cuisine, Allergen, Ingredient, RecipeAllergen, RecipeIngredient
from schemas import Item, FilterParams, FormData, RecipeCreate, RecipeUpdate, RecipeResponse
from fastapi import FastAPI, APIRouter, Path, Query, Form, File, UploadFile, HTTPException, status, Depends
from config import settings
from typing import Annotated, List
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(
    tags=["Lab1"],
    prefix=settings.url.lab1a1,
)

# ЧАСТЬ А1 ЧАСТЬ А1 ЧАСТЬ А1 ЧАСТЬ А1

@router.post("/Body/")
async def create_item(item: Item):
    return item

@router.get("/QueryParamsAndValidation/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@router.get("/PathParamsAndValidation/{item_id}")
async def read_items(
    *,
    item_id: Annotated[int, Path(description="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5, description="Size must be between 0 and 10.5")]
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results

@router.get("/QueryParamsModels/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@router.put("/NestedModels/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

@router.post("/RequestForms/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}

@router.post("/RequstFormModels/")
async def login(data: Annotated[FormData, Form()]):
    return data

# ЧАСТЬ А2 ЧАСТЬ А2 ЧАСТЬ А2 ЧАСТЬ А2

@router.get("/format-test")
async def get_data_view(format: str = Query("json", regex="^(json|html)$")):
    data = {"message": "Hello from FastAPI!", "status": "success"}
    
    if format == "html":
        html_content = f"""
        <html>
            <body>
                <h1>Data Response</h1>
                <p>Message: {data['message']}</p>
                <p>Status: {data['status']}</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    return data

# ЧАСТЬ А3 ЧАСТЬ А3 ЧАСТЬ А3 ЧАСТЬ А3


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if not allowed_file(file.filename or ""):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Allowed: PNG, JPG, JPEG, WEBP"
        )

    # генерация уникального имени
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / filename

    # сохранение
    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_url = f"/uploads/{filename}"
    return {"url": file_url}

# ЧАСТЬ B ЧАСТЬ B ЧАСТЬ B ЧАСТЬ B

# Create
@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: RecipeCreate,
    session: AsyncSession = Depends(db_helper.session_getter)
):
    # Create the recipe with base fields
    recipe_data = recipe.model_dump(exclude={'allergen_ids', 'ingredients'})
    db_recipe = Recipe(**recipe_data)
    session.add(db_recipe)
    
    # We need to flush to get the recipe ID
    await session.flush()
    
    # Add allergen associations
    for allergen_id in recipe.allergen_ids:
        recipe_allergen = RecipeAllergen(recipe_id=db_recipe.id, allergen_id=allergen_id)
        session.add(recipe_allergen)
    
    # Add ingredient associations
    for ingredient_input in recipe.ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=db_recipe.id,
            ingredient_id=ingredient_input.ingredient_id,
            quantity=ingredient_input.quantity,
            measurement=ingredient_input.measurement
        )
        session.add(recipe_ingredient)
    
    await session.commit()
    await session.refresh(db_recipe)
    
    return await build_recipe_response(db_recipe, session)

# Helper function to build recipe response with nested data
async def build_recipe_response(recipe: Recipe, session: AsyncSession):
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
    recipe_ingredients_result = await session.execute(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
    )
    recipe_ingredients = recipe_ingredients_result.scalars().all()
    
    ingredients = [
        {
            "id": ri.ingredient_id,
            "quantity": ri.quantity,
            "measurement": ri.measurement
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
        "ingredients": ingredients
    }


# Read all
@router.get("/", response_model=List[RecipeResponse])
async def read_recipes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Recipe).offset(skip).limit(limit))
    recipes = result.scalars().all()
    
    response = []
    for recipe in recipes:
        recipe_response = await build_recipe_response(recipe, session)
        response.append(recipe_response)
    
    return response


# Read by ID
@router.get("/{recipe_id}", response_model=RecipeResponse)
async def read_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return await build_recipe_response(recipe, session)

# Update
@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe_update: RecipeUpdate,
    session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    db_recipe = result.scalar_one_or_none()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)

    await session.commit()
    await session.refresh(db_recipe)
    return db_recipe

# Delete
@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(db_helper.session_getter)
):
    result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    db_recipe = result.scalar_one_or_none()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    await session.delete(db_recipe)
    await session.commit()
    return  # 204 — без тела