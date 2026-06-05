from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ainovel",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "recalculate-rankings-hourly": {
            "task": "recalculate_rankings",
            "schedule": 3600.0,
        },
        "flush-view-counts-5min": {
            "task": "flush_view_counts",
            "schedule": 300.0,
        },
    },
)
