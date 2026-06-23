from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.enums import AssetStatus, AssetType


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    value: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE
    )
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

