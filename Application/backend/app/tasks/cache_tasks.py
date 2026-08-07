# ----------------------------------------------------
# ClubConnect AI Module
# Integrated by AI Backend
# Module Owner: AI Assistant / RAG Pipeline
# ----------------------------------------------------
"""Phase 6A - lightweight scheduled maintenance: expired AI-cache cleanup.

The only Celery job introduced by Phase 6A (see CHANGELOG.md /
NEXT_PHASE.md). No cache warming, no embedding rebuilds, no
recommendation rebuilding, no advanced scheduling - just one small
cleanup job, scheduled from app/core/celery.py's beat_schedule.
"""
from app.core.celery import celery_app
from app.modules.ai_services.cache import cleanup_expired_keys


@celery_app.task(name="app.tasks.cache_tasks.cleanup_expired_cache")
def cleanup_expired_cache() -> int:
    """Celery entry point. Business logic lives in
    cache.cleanup_expired_keys() so it's unit-testable without a
    running Celery worker - this wrapper just registers it as a task.
    """
    return cleanup_expired_keys()
