from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from api.deps import get_current_organization
from core.database import get_db
from models.organization import Organization
from schemas.asset import (
    AssetCreate,
    AssetGraphResponse,
    AssetListParams,
    AssetRead,
    AssetUpdate,
    PaginatedAssetResponse,
)
from services.assets import create_asset
from services.assets import delete_asset
from services.assets import get_asset
from services.assets import get_asset_graph
from services.assets import list_assets
from services.assets import update_asset
from services.assets import get_expiring_soon_assets as get_expiring_soon_assets_service
from services.assets import get_expired_assets as get_expired_assets_service

router = APIRouter()


@router.get("/", response_model=PaginatedAssetResponse)
def get_assets(
    params: Annotated[AssetListParams, Query()],
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return list_assets(db, current_org.id, params)


@router.get("/expiring-soon")
def get_expiring_soon_assets(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
) :
    return get_expiring_soon_assets_service(db, current_org.id)


@router.get("/expired")
def get_expired_assets(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
) :
    return get_expired_assets_service(db, current_org.id)


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset_by_id(
    asset_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return get_asset(db, current_org.id, asset_id)


@router.post("/", response_model=AssetRead)
def create_asset_route(
    data: AssetCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    asset, created = create_asset(db, current_org.id, data)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset_route(
    asset_id: str,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return update_asset(db, current_org.id, asset_id, data)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset_route(
    asset_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    delete_asset(db, current_org.id, asset_id)


@router.get("/{asset_id}/graph", response_model=AssetGraphResponse)
def get_asset_graph_route(
    asset_id: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return get_asset_graph(db, current_org.id, asset_id)


