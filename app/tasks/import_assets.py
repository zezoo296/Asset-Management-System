from services.assets import import_assets
from core.database import SessionLocal
from celery_app import celery

@celery.task
def process_assets_import(organization_id, data, job_id):
    db = SessionLocal()
    try:
        return import_assets(db, organization_id, data, job_id)
    finally:
        db.close()