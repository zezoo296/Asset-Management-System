from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.relation import Relation
from schemas.relation import RelationCreate


def get_relations(db: Session, organization_id: UUID) -> list[Relation]:
    return (
        db.query(Relation)
        .filter(Relation.organization_id == organization_id)
        .all()
    )


def get_asset_relations(
    db: Session,
    organization_id: UUID,
    asset_id: str,
) -> list[Relation]:
    return (
        db.query(Relation)
        .filter(
            Relation.organization_id == organization_id,
            or_(Relation.from_id == asset_id, Relation.to_id == asset_id),
        )
        .all()
    )


def create_relation(
    db: Session,
    organization_id: UUID,
    data: RelationCreate,
) -> Relation:
    relation = Relation(
        from_id=data.from_id,
        to_id=data.to_id,
        type=data.type,
        organization_id=organization_id,
    )
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation
