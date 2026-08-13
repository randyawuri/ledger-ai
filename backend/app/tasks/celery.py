from celery import Celery

from app.core.config import settings


celery = Celery(
    "ledgerai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Import task modules so Celery registers them
import app.tasks.transaction_tasks  # noqa: F401

celery.autodiscover_tasks(
    [
        "app.tasks",
    ]
)