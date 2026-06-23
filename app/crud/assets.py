from uuid import UUID

from sqlalchemy.orm import Session

from models.asset import Asset
from schemas.asset import AssetListParams

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
