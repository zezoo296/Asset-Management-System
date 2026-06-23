from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_organization
from core.database import get_db
from models.organization import Organization
from schemas.asset import AssetListParams, PaginatedAssetResponse
from services.assets import list_assets

router = APIRouter()


@router.get("/", response_model=PaginatedAssetResponse)
def get_assets(
    params: Annotated[AssetListParams, Query()],
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return list_assets(db, current_org.id, params)
