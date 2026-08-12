# ----------------------------------------------------
# ClubConnect AI Module
# Integrated by AI Backend
# Module Owner: AI Assistant / RAG Pipeline
# (Celery app instance - used solely for the scheduled
#  AI cache-cleanup job)
# ----------------------------------------------------
"""Celery app instance (Phase 6A).

Introduced solely to run one lightweight scheduled maintenance job -
expired AI-cache-key cleanup (see app/tasks/cache_tasks.py). This is
not a general task-queue build-out; nothing else in the codebase uses
Celery. Per Phase 6A scope: no cache warming, no embedding rebuilds,
no recommendation rebuilding, no advanced scheduling.
"""
import os

from celery import Celery
from celery.schedules import crontab

_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0")
)
_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", _BROKER_URL)

celery_app = Celery("clubconnect", broker=_BROKER_URL, backend=_RESULT_BACKEND)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Single scheduled job for Phase 6A - see app/tasks/cache_tasks.py. Every
# 30 minutes is plenty for a cleanup task whose only job is pruning stale
# key references (the cache entries themselves already expire via Redis
# TTL regardless of whether this task ever runs).
celery_app.conf.beat_schedule = {
    "cleanup-expired-ai-cache": {
        "task": "app.tasks.cache_tasks.cleanup_expired_cache",
        "schedule": crontab(minute="*/30"),
    }
}
