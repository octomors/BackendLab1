from models import Item
from fastapi import FastAPI, APIRouter, status
from config import settings

router = APIRouter(
    tags=["Lab1A1"],
    prefix=settings.url.lab1a1,
)

@router.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item