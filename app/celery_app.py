from celery import Celery
from core.config import CELERY_BROKER_URL

celery = Celery(
    "Worker",
    broker=CELERY_BROKER_URL,
    include=["tasks.import_assets"],
)

celery.autodiscover_tasks(["tasks"])