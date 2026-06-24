from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String
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
