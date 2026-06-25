from datetime import date, datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy import cast, Date
from sqlalchemy.orm import Session

from core.config import EXPIRING_SOON_DAYS
from models.asset import Asset
from models.enums import AssetStatus, AssetType
from schemas.asset import AssetCreate, AssetListParams, AssetUpsertData

SORTABLE_COLUMNS = {
    "type": Asset.type,
    "status": Asset.status,
    "value": Asset.value,
    "first_seen": Asset.first_seen,
    "last_seen": Asset.last_seen,
}


def get_assets(
    db: Session,
    organization_id: UUID,
    params: AssetListParams,
) -> tuple[list[Asset], int]:
    query = db.query(Asset).filter(Asset.organization_id == organization_id)

    if params.type is not None:
        query = query.filter(Asset.type == params.type)
    if params.status is not None:
        query = query.filter(Asset.status == params.status)
    if params.tag is not None:
        query = query.filter(Asset.tags.contains([params.tag]))
    if params.value is not None:
        query = query.filter(Asset.value.ilike(f"%{params.value}%"))

    total = query.count()

    sort_column = SORTABLE_COLUMNS[params.sort_by]
    if params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (params.page - 1) * params.limit
    items = query.offset(offset).limit(params.limit).all()

    return items, total


def get_asset_by_id(
    db: Session,
    organization_id: UUID,
    asset_id: str,
) -> Asset | None:
    return (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.organization_id == organization_id)
        .first()
    )


def get_asset_by_unique_key(
    db: Session,
    organization_id: UUID,
    asset_type: AssetType,
    value: str,
) -> Asset | None:
    return (
        db.query(Asset)
        .filter(
            Asset.organization_id == organization_id,
            Asset.type == asset_type,
            Asset.value == value,
        )
        .first()
    )


def create_asset(
    db: Session,
    organization_id: UUID,
    data: AssetCreate,
    commit: bool = True,
) -> Asset:
    now = datetime.now(timezone.utc)
    asset = Asset(
        id=data.id,
        type=data.type,
        value=data.value,
        status=data.status,
        source=[data.source],
        tags=list(data.tags),
        metadata_=dict(data.metadata),
        organization_id=organization_id,
        first_seen=now,
        last_seen=now,
    )
    db.add(asset)
    if commit:
        db.commit()
    else:
        db.flush()
    return asset


def update_asset(
    db: Session,
    existing: Asset,
    incoming: AssetUpsertData,
    commit: bool = True
) -> Asset:
    if(incoming.metadata):
        existing.metadata_ = {**existing.metadata_, **incoming.metadata}

    if incoming.source and incoming.source not in existing.source:
        existing.source = existing.source + [incoming.source]

    if(incoming.tags):
        merged_tags = list(existing.tags)
        for tag in incoming.tags:
            if tag not in merged_tags:
                merged_tags.append(tag)
        existing.tags = merged_tags

    if existing.status == AssetStatus.STALE:
        existing.status = AssetStatus.ACTIVE

    if incoming.status:
        existing.status = incoming.status

    if existing.type == AssetType.CERTIFICATE and incoming.metadata and "expires" in incoming.metadata:
        existing.metadata_["expires"] = incoming.metadata["expires"]

    existing.last_seen = datetime.now(timezone.utc)

    if commit:
        db.commit()
    else:
        db.flush()
    return existing


def delete_asset(db: Session, asset: Asset) -> None:
    db.delete(asset)
    db.commit()


def get_expiring_soon_assets(db: Session, organization_id: UUID):
    today = date.today()
    cutoff = today + timedelta(days=int(EXPIRING_SOON_DAYS))

    expires = cast(Asset.metadata_["expires"].astext, Date)
    assets = (
        db.query(Asset)
        .filter(Asset.organization_id == organization_id)
        .filter(Asset.type == AssetType.CERTIFICATE)
        .filter(Asset.metadata_["expires"].is_not(None))
        .filter(expires.between(today, cutoff))
        .all()
    )
    return assets



def get_expired_assets(db: Session, organization_id: UUID):
    today = date.today()
    expires = cast(Asset.metadata_["expires"].astext, Date)
    
    assets = (
        db.query(Asset)
        .filter(Asset.organization_id == organization_id)
        .filter(Asset.type == AssetType.CERTIFICATE)
        .filter(Asset.metadata_["expires"].is_not(None))
        .filter(expires < today)
        .all()
    )
    return assets