"""
Celery application configuration and task definitions.
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Initialize Celery
celery_app = Celery(
    "cryptoflyt",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    'check-price-alerts': {
        'task': 'app.workers.tasks.check_price_alerts',
        'schedule': 60.0,  # Run every 60 seconds
    },
    'update-price-history': {
        'task': 'app.workers.tasks.update_price_history',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

if __name__ == '__main__':
    celery_app.start()
