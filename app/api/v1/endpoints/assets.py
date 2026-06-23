from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_organization
from core.database import get_db
from models.organization import Organization
from schemas.asset import AssetListParams, AssetRead, PaginatedAssetResponse
from services.assets import get_asset
from services.assets import list_assets

router = APIRouter()


@router.get("/", response_model=PaginatedAssetResponse)
def get_assets(
    params: Annotated[AssetListParams, Query()],
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return list_assets(db, current_org.id, params)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset_by_id(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return get_asset(db, current_org.id, asset_id)