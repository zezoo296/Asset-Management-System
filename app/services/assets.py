import math
from collections import deque
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from crud.assets import create_asset as create_asset_crud
from crud.assets import delete_asset as delete_asset_crud
from crud.assets import get_asset_by_id
from crud.assets import get_asset_by_unique_key, get_expiring_soon_assets as get_expiring_soon_assets_crud
from crud.assets import get_assets as get_assets_crud, get_expired_assets as get_expired_assets_crud
from crud.assets import update_asset as update_asset_crud
from crud.relations import get_asset_relations
from crud.relations import create_relation as create_relation_crud
from models.asset import Asset
from models.enums import AssetType, RelationType

from schemas.asset import (
    AssetCreate,
    AssetGraphEdge,
    AssetGraphNode,
    AssetGraphResponse,
    AssetListParams,
    AssetUpdate,
    PaginatedAssetResponse,
)
from schemas.relation import RelationCreate


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
    asset = get_asset_by_id(db, organization_id, asset_id)
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
    commit: bool = True,
) :
    existing = get_asset_by_unique_key(
        db, organization_id, data.type, data.value
    )
    if existing is not None:
        updated = update_asset_crud(db, existing, data, commit=commit)
        return updated, False

    created = create_asset_crud(db, organization_id, data, commit=commit)
    return created, True


def extract_asset_relations(
    asset: AssetCreate,
    relations: list[RelationCreate],
) -> None:
    if asset.type == AssetType.SUBDOMAIN:
        if asset.parent:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.parent,
                type=RelationType.PARENT,
            ))
        if asset.resolves_to:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.resolves_to,
                type=RelationType.RESOLVES_TO,
            ))
    elif asset.type == AssetType.CERTIFICATE:
        if asset.covers:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.covers,
                type=RelationType.COVERS,
            ))
    elif asset.type == AssetType.IP_ADDRESS:
        if asset.resolved_from:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.resolved_from,
                type=RelationType.RESOLVED_FROM,
            ))
    elif asset.type == AssetType.SERVICE:
        if asset.runs_on:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.runs_on,
                type=RelationType.RUNS_ON,
            ))
    elif asset.type == AssetType.TECHNOLOGY:
        if asset.detected_on:
            relations.append(RelationCreate(
                from_id=asset.id,
                to_id=asset.detected_on,
                type=RelationType.DETECTED_ON,
            ))



def import_assets(
    db: Session,
    organization_id: UUID,
    data: list[dict],
) -> dict:
    response = {
        "created": 0,
        "updated": 0,
        "relationships_created": 0,
        "failed": 0,
        "errors": [],
    }
    relations = []

    for item in data:
        try:
            asset_data = AssetCreate.model_validate(item)
        except ValidationError as e:
            response["failed"] += 1
            response["errors"].append({
                "asset": item.get("id"),
                "error": "Validation failed.",
                "details": e.errors(),
            })
            continue

        try:
            with db.begin_nested():
                _, is_new = create_asset(db, organization_id, asset_data, commit=False)
                if is_new:
                    response["created"] += 1
                else:
                    response["updated"] += 1

                extract_asset_relations(asset_data, relations)

        except Exception as e:
            response["failed"] += 1
            response["errors"].append({
                "asset": item.get("id"),
                "error": "Failed to import asset.",
            })
            continue
    db.commit()

    for relation in relations:
        try:
            with db.begin_nested():
                create_relation_crud(db, organization_id, relation, commit=False)
                response["relationships_created"] += 1
        except IntegrityError as e:
            if isinstance(e.orig, ForeignKeyViolation):
                response["errors"].append({
                    "relation": relation.from_id,
                    "error": f"Referenced asset '{relation.to_id}' does not exist."
                })
            else:
                response["errors"].append({
                    "relation": relation.from_id,
                    "error": "Database integrity error."
                })
        except Exception as e:
            response["errors"].append({
                "relation": relation.from_id,
                "error": "Unexpected error while creating relation."
            })
    db.commit()

    return response
  

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


def get_asset_graph(
    db: Session,
    organization_id: UUID,
    root_asset_id: str,
) -> AssetGraphResponse:
    root_asset = get_asset(db, organization_id, root_asset_id)

    nodes: dict[str, Asset] = {root_asset.id: root_asset}
    edges: dict[tuple[str, str, str], AssetGraphEdge] = {}
    visited: set[str] = set()
    queue: deque[str] = deque([root_asset.id])

    while queue:
        current_id = queue.popleft()

        if current_id in visited:
            continue
        visited.add(current_id)

        relations = get_asset_relations(db, organization_id, current_id)

        for relation in relations:
            edge_key = (relation.from_id, relation.to_id, relation.type.value)
            if edge_key not in edges:
                edges[edge_key] = AssetGraphEdge.model_validate(relation)

            for neighbor_id in (relation.from_id, relation.to_id):
                if neighbor_id not in nodes:
                    asset = get_asset_by_id(db, organization_id, neighbor_id)
                    if asset is not None:
                        nodes[neighbor_id] = asset
                        queue.append(neighbor_id)

    return AssetGraphResponse(
        root_asset_id=root_asset_id,
        nodes=[
            AssetGraphNode.model_validate(asset)
            for asset in nodes.values()
        ],
        edges=list(edges.values()),
    )

def get_expiring_soon_assets(db: Session, organization_id: UUID):
    return get_expiring_soon_assets_crud(db, organization_id)

def get_expired_assets(db: Session, organization_id: UUID):
    return get_expired_assets_crud(db, organization_id)
