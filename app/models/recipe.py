from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Text, Integer, CheckConstraint, ForeignKey
from typing import Optional

from .base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    cuisine_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cuisines.id"), nullable=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5", name="check_difficulty_range"
        ),
    )

    def __repr__(self):
        return f"Recipe(id={self.id}, title={self.title})"
