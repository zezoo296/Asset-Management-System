from celery import Celery
from core.config import CELERY_BROKER_URL

celery = Celery(
    "Worker",
    broker=CELERY_BROKER_URL,
    include=["tasks.import_assets"],
)

celery.autodiscover_tasks(["tasks"])

celery.conf.update(
    # Heartbeat once per minute (instead of every 10s)
    broker_heartbeat=120,

    # Transport options to reduce polling overhead
    broker_transport_options={
        "visibility_timeout": 3600,  # 1 hour
    },

    # Retry connection on startup
    broker_connection_retry_on_startup=True,
)
