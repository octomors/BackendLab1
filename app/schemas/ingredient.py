from pydantic import BaseModel, Field
from typing import Optional


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        from_attributes = True
