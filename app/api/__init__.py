from fastapi import APIRouter

from config import settings

from .test import router as test_router
from .posts import router as posts_router
from .lab1 import router as lab1_router
from .lab2 import router as lab2_router
from .auth import router as auth_router
from .users import router as users_router

router = APIRouter(
    prefix=settings.url.prefix,
)
#router.include_router(test_router)
#router.include_router(posts_router)
router.include_router(lab1_router)
router.include_router(lab2_router)
router.include_router(auth_router)
router.include_router(users_router)
