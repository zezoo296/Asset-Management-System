from fastapi import APIRouter
from .endpoints.assets import router as assets_router
from .endpoints.auth import router as auth_router
from .endpoints.relations import router as relations_router

router = APIRouter()

router.include_router(assets_router, prefix="/assets", tags=["assets"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(relations_router, prefix="/relations", tags=["relations"])