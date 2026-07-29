import math
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.import_jobs import get_import_jobs as get_import_jobs_crud
from crud.import_jobs import get_import_job_by_id, add_import_job
from models.import_job import ImportJob
from schemas.import_job import ImportJobListParams, PaginatedImportJobResponse
from tasks.import_assets import process_assets_import


def list_import_jobs(
    db: Session, organization_id: UUID, params: ImportJobListParams
) -> PaginatedImportJobResponse:
    items, total = get_import_jobs_crud(db, organization_id, params)
    pages = math.ceil(total / params.limit) if total else 0

    return PaginatedImportJobResponse(
        items=items,
        total=total,
        page=params.page,
        limit=params.limit,
        pages=pages,
    )


def get_import_job(
    db: Session, organization_id: UUID, job_id: UUID
) -> ImportJob:
    job = get_import_job_by_id(db, organization_id, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found",
        )
    return job

def import_assets(
    db: Session, organization_id: UUID, assets: list[dict]
):
    job = add_import_job(db, organization_id, len(assets))
    process_assets_import.delay(organization_id, assets, job.id)
    return job