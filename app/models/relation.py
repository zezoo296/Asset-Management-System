from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.enums import RelationType


class Relation(Base):
    __tablename__ = "relations"

    from_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    to_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    type: Mapped[RelationType] = mapped_column(
        Enum(RelationType), primary_key=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
