from pydantic import BaseModel, Field
from typing import Optional, List


class RecipeIngredientInput(BaseModel):
    ingredient_id: int
    quantity: float = Field(..., gt=0)
    measurement: int = Field(..., ge=1, le=3)


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    cooking_time: int = Field(..., gt=0)
    difficulty: int = Field(..., ge=1, le=5)


class RecipeCreate(RecipeBase):
    cuisine_id: Optional[int] = None
    allergen_ids: List[int] = []
    ingredients: List[RecipeIngredientInput] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)


class CuisineInRecipe(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class AllergenInRecipe(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class IngredientInRecipe(BaseModel):
    id: int
    quantity: float
    measurement: int

    class Config:
        from_attributes = True


class RecipeResponse(RecipeBase):
    id: int
    cuisine: Optional[CuisineInRecipe] = None
    allergens: List[AllergenInRecipe] = []
    ingredients: List[IngredientInRecipe] = []

    class Config:
        from_attributes = True