from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.enums import RelationType


class RelationBase(BaseModel):
    from_id: str
    to_id: str
    type: RelationType


class RelationCreate(RelationBase):
    pass


class RelationRead(RelationBase):
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)
