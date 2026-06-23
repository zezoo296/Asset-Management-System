from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import AssetStatus, AssetType


class AssetBase(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.ACTIVE
    source: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    organization_id: UUID


class AssetCreate(AssetBase):
    first_seen: datetime | None = None
    last_seen: datetime | None = None


class AssetUpdate(BaseModel):
    type: AssetType | None = None
    value: str | None = None
    status: AssetStatus | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    source: list[str] | None = None
    tags: list[str] | None = None
    metadata: dict | None = None
    organization_id: UUID | None = None


class AssetRead(AssetBase):
    id: UUID
    first_seen: datetime
    last_seen: datetime
    metadata: dict = Field(validation_alias="metadata_")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AssetListParams(BaseModel):
    type: AssetType | None = None
    status: AssetStatus | None = None
    tag: str | None = None
    value: str | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["type", "status", "value", "first_seen", "last_seen"] = "last_seen"
    sort_order: Literal["asc", "desc"] = "desc"


class PaginatedAssetResponse(BaseModel):
    items: list[AssetRead]
    total: int
    page: int
    limit: int
    pages: int
