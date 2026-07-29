from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.import_job import ImportJob
from models.enums import ImportJobStatus
from schemas.import_job import ImportJobListParams


def get_import_jobs(
    db: Session, organization_id: UUID, params: ImportJobListParams
) -> tuple[list[ImportJob], int]:
    query = db.query(ImportJob).filter(ImportJob.organization_id == organization_id)

    if params.status is not None:
        query = query.filter(ImportJob.status == params.status)

    total = query.count()
    offset = (params.page - 1) * params.limit
    items = (
        query.order_by(ImportJob.started_at.desc())
        .offset(offset)
        .limit(params.limit)
        .all()
    )
    return items, total


def get_import_job_by_id(
    db: Session, organization_id: UUID, job_id: UUID
) -> ImportJob | None:
    return (
        db.query(ImportJob)
        .filter(
            ImportJob.id == job_id,
            ImportJob.organization_id == organization_id,
        )
        .first()
    )

def add_import_job(
    db: Session, organization_id: UUID, total_rows: int
) -> ImportJob :
    job = ImportJob(
        organization_id=organization_id,
        total_rows=total_rows
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def update_import_job_progress(
    db: Session,
    job_id: UUID,
    processed_rows: int,
    response: dict,
    finished: bool = False,
) -> None:
    values = {
        ImportJob.processed_rows: processed_rows,
        ImportJob.created_count: response["created"],
        ImportJob.updated_count: response["updated"],
        ImportJob.relationships_created_count: response[
            "relationships_created"
        ],
        ImportJob.failed_count: response["failed"],
    }
    if finished:
        values.update(
            {
                ImportJob.status: ImportJobStatus.SUCCESS,
                ImportJob.finished_at: datetime.now(timezone.utc),
            }
        )

    (
        db.query(ImportJob)
        .filter(ImportJob.id == job_id)
        .update(
            values,
            synchronize_session=False,
        )
    )
    db.commit()
