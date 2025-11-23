from pydantic import BaseModel, Field
from typing import Optional


class CuisineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class CuisineCreate(CuisineBase):
    pass


class CuisineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class CuisineResponse(CuisineBase):
    id: int

    class Config:
        from_attributes = True
