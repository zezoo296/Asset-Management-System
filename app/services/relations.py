from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud.relations import create_relation as create_relation_crud
from crud.relations import get_relations as get_relations_crud
from models.relation import Relation
from schemas.relation import RelationCreate


def list_relations(db: Session, organization_id: UUID) -> list[Relation]:
    return get_relations_crud(db, organization_id)


def create_relation(
    db: Session,
    organization_id: UUID,
    data: RelationCreate,
) -> Relation:
    try:
        return create_relation_crud(db, organization_id, data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create relation: invalid asset reference or relation already exists",
        ) from exc
