from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.enums import ImportJobStatus


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ImportJobStatus] = mapped_column(
        Enum(ImportJobStatus), nullable=False, default=ImportJobStatus.PENDING
    )
    processed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    relationships_created_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
