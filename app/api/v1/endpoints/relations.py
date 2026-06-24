from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.deps import get_current_organization
from core.database import get_db
from models.organization import Organization
from schemas.relation import RelationCreate, RelationRead
from services.relations import create_relation
from services.relations import list_relations

router = APIRouter()


@router.get("/", response_model=list[RelationRead])
def get_relations(
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return list_relations(db, current_org.id)


@router.post("/", response_model=RelationRead, status_code=status.HTTP_201_CREATED)
def create_relation_route(
    data: RelationCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    return create_relation(db, current_org.id, data)
