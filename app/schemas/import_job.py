from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import ImportJobStatus


class ImportJob(BaseModel):
    id: UUID
    organization_id: UUID
    celery_task_id: str | None
    status: ImportJobStatus
    processed_rows: int
    total_rows: int
    created_count: int
    updated_count: int
    relationships_created_count: int
    failed_count: int
    started_at: datetime
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ImportJobListParams(BaseModel):
    status: ImportJobStatus | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedImportJobResponse(BaseModel):
    items: list[ImportJob]
    total: int
    page: int
    limit: int
    pages: int
