"""
Celery worker application factory and Redis telemetry pub/sub broadcaster.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from celery import Celery
import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "untangle_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.ingestion"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minute hard ceiling for massive books
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
    broker_connection_timeout=1.0,
)


def publish_telemetry(document_id: str, payload: dict[str, Any]) -> None:
    """
    Publish real-time ingestion telemetry to Redis pub/sub channel.

    The Vue frontend and FastAPI WebSockets subscribe to `doc:{document_id}:progress`
    to animate the 3-step building pipeline in real-time.
    """
    try:
        r = redis.from_url(settings.redis_url)
        channel = f"doc:{document_id}:progress"
        message_bytes = json.dumps(payload).encode("utf-8")
        r.publish(channel, message_bytes)
        logger.debug("Published telemetry to %s: %s", channel, payload.get("current_step"))
    except (redis.RedisError, OSError) as exc:
        logger.debug("Redis pub/sub publish skipped/deferred: %s", exc)

