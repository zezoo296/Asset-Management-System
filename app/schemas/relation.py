from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.enums import RelationType


class RelationBase(BaseModel):
    from_id: UUID
    to_id: UUID
    type: RelationType


class RelationCreate(RelationBase):
    pass


class RelationRead(RelationBase):
    model_config = ConfigDict(from_attributes=True)
