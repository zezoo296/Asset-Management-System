from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class OrganizationBase(BaseModel):
    name: str
    email: EmailStr


class OrganizationCreate(OrganizationBase):
    password: str



class OrganizationRead(OrganizationBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
