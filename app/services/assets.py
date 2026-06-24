import math
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.assets import create_asset as create_asset_crud
from crud.assets import delete_asset as delete_asset_crud
from crud.assets import get_asset_by_id as get_asset_by_id_crud
from crud.assets import get_asset_by_unique_key
from crud.assets import get_assets as get_assets_crud
from crud.assets import update_asset as update_asset_crud
from models.asset import Asset
from schemas.asset import AssetCreate, AssetListParams, AssetUpdate, PaginatedAssetResponse


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


def get_asset(db: Session, organization_id: UUID, asset_id: str) -> Asset:
    asset = get_asset_by_id_crud(db, organization_id, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return asset


def create_asset(
    db: Session,
    organization_id: UUID,
    data: AssetCreate,
) -> tuple[Asset, bool]:
    existing = get_asset_by_unique_key(
        db, organization_id, data.type, data.value
    )
    if existing is not None:
        updated = update_asset_crud(db, existing, data)
        return updated, False

    created = create_asset_crud(db, organization_id, data)
    return created, True


def update_asset(
    db: Session,
    organization_id: UUID,
    asset_id: str,
    data: AssetUpdate,
) -> Asset:
    existing = get_asset(db, organization_id, asset_id)
    return update_asset_crud(db, existing, data)


def delete_asset(
    db: Session,
    organization_id: UUID,
    asset_id: str,
) -> None:
    asset = get_asset(db, organization_id, asset_id)
    delete_asset_crud(db, asset)
