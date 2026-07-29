from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from api.deps import get_current_organization
from core.database import get_db
from models.organization import Organization
from schemas.import_job import ImportJobListParams, PaginatedImportJobResponse
from schemas.import_job import ImportJob
from services.asset_imports import get_import_job, list_import_jobs, import_assets as enqueue_asset_import

router = APIRouter()


@router.get("/", response_model=PaginatedImportJobResponse)
def get_asset_import_jobs(
    params: Annotated[ImportJobListParams, Query()],
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
) -> PaginatedImportJobResponse:
    return list_import_jobs(db, current_org.id, params)


@router.get("/{job_id}", response_model=ImportJob)
def get_asset_import_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
) -> ImportJob:
    return get_import_job(db, current_org.id, job_id)

@router.post("/")
def add_asset_import_job(
    data: list[dict],
    response: Response,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
):
    job = enqueue_asset_import(db, current_org.id, data)
    response.status_code = status.HTTP_202_ACCEPTED
    return {"job_id": job.id, "message": "Assets recieved."}