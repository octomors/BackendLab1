from pydantic import BaseModel, Field
from typing import Optional


class AllergenBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class AllergenCreate(AllergenBase):
    pass


class AllergenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class AllergenResponse(AllergenBase):
    id: int

    class Config:
        from_attributes = True
