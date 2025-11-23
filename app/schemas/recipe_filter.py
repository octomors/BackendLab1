from pydantic import BaseModel, Field
from typing import Optional, List


class RecipeFilter(BaseModel):
    """
    Filter for Recipe model.
    Supports:
    - name__like (or title__like): Full-text search by recipe name/title
    - ingredient_id: Filter by ingredient IDs (comma-separated list)
    - order_by: Sort by field (default: ["-id"])
    """
    
    # Support both name__like and title__like for compatibility
    name__like: Optional[str] = None
    title__like: Optional[str] = None
    ingredient_id: Optional[List[int]] = None
    order_by: List[str] = Field(default_factory=lambda: ["-id"])
