from fastapi import APIRouter, Depends
from .endpoints.assets import router as assets_router
from .endpoints.auth import router as auth_router
from .endpoints.relations import router as relations_router
from .endpoints.asset_imports import router as asset_imports_router
from api.deps import identify_consumer

authenticated_router = APIRouter(dependencies=[Depends(identify_consumer)])

authenticated_router.include_router(assets_router, prefix="/assets", tags=["assets"])
authenticated_router.include_router(asset_imports_router, prefix="/asset-imports", tags=["asset-imports"])
authenticated_router.include_router(relations_router, prefix="/relations", tags=["relations"])

router = APIRouter()

router.include_router(authenticated_router)
router.include_router(auth_router, prefix="/auth", tags=["auth"])