import math
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.assets import get_asset_by_id as get_asset_by_id_crud
from crud.assets import get_assets as get_assets_crud
from models.asset import Asset
from schemas.asset import AssetListParams, PaginatedAssetResponse


def list_assets(
    db: Session,
    organization_id: UUID,
    params: AssetListParams,
) -> PaginatedAssetResponse:
    items, total = get_assets_crud(db, organization_id, params)
    pages = math.ceil(total / params.limit) if total > 0 else 0

    return PaginatedAssetResponse(
        items=items,
        total=total,
        page=params.page,
        limit=params.limit,
        pages=pages,
    )


def get_asset(db: Session, organization_id: UUID, asset_id: UUID) -> Asset:
    asset = get_asset_by_id_crud(db, organization_id, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return asset
