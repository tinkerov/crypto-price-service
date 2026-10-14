from celery import Celery
from celery.schedules import crontab

from app.config import settings


celery_app = Celery(
    "crypto_price_service",
    broker=settings.redis_url,
    include=["app.tasks.price_collector"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-crypto-prices-every-minute": {
            "task": "app.tasks.price_collector.collect_prices",
            "schedule": crontab(minute="*"),
        },
    },
)