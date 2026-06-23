from fastapi import APIRouter
from .endpoints.assets import router as assets_router
from .endpoints.auth import router as auth_router

router = APIRouter()

router.include_router(assets_router, prefix="/assets", tags=["assets"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])