from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from .base import Base


class RecipeAllergen(Base):
    __tablename__ = "recipe_allergens"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    allergen_id: Mapped[int] = mapped_column(
        ForeignKey("allergens.id"), primary_key=True
    )

    def __repr__(self):
        return f"RecipeAllergen(recipe_id={self.recipe_id}, allergen_id={self.allergen_id})"
