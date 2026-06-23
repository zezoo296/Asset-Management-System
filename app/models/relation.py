from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.enums import RelationType


class Relation(Base):
    __tablename__ = "relations"

    from_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), primary_key=True
    )
    to_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), primary_key=True
    )
    type: Mapped[RelationType] = mapped_column(
        Enum(RelationType), primary_key=True
    )
