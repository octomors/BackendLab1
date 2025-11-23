from fastapi import APIRouter

from config import settings

from .test import router as test_router
from .posts import router as posts_router
from .lab1 import router as lab1_router

router = APIRouter(
    prefix=settings.url.prefix,
)
router.include_router(test_router)
router.include_router(posts_router)
router.include_router(lab1_router)