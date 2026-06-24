from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import AssetSource, AssetStatus, AssetType, RelationType


class AssetUpsertData(BaseModel):
    type: AssetType
    value: str
    status: AssetStatus = AssetStatus.ACTIVE
    source: AssetSource
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AssetCreate(AssetUpsertData):
    id: str


class AssetUpdate(BaseModel):
    type: AssetType | None = None
    value: str | None = None
    status: AssetStatus | None = None
    source: AssetSource | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class AssetRead(BaseModel):
    id: str 
    type: AssetType
    value: str
    status: AssetStatus
    source: list[AssetSource] 
    tags: list[str]
    metadata: dict = Field(validation_alias="metadata_")
    organization_id: UUID
    first_seen: datetime
    last_seen: datetime

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


class AssetGraphNode(BaseModel):
    id: str
    type: AssetType
    value: str
    status: AssetStatus
    source: list[AssetSource]
    tags: list[str]
    metadata: dict = Field(validation_alias="metadata_")
    first_seen: datetime
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AssetGraphEdge(BaseModel):
    from_id: str = Field(serialization_alias="from")
    to_id: str = Field(serialization_alias="to")
    type: RelationType

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, ser_json_by_alias=True)


class AssetGraphResponse(BaseModel):
    root_asset_id: str
    nodes: list[AssetGraphNode]
    edges: list[AssetGraphEdge]
