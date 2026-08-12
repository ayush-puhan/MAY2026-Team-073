# ----------------------------------------------------
# ClubConnect AI Module
# Integrated by AI Backend
# Module Owner: AI Assistant / RAG Pipeline
# (Redis client singleton - used by the AI response cache /
#  conversation memory and the cache-cleanup Celery task)
# ----------------------------------------------------
"""Redis client singleton (Phase 6A).

Used by ``app/modules/ai_services/cache.py`` for the AI response cache
and short conversation memory, and by the Celery cleanup task
(``app/tasks/cache_tasks.py``). Nothing else in the codebase depends on
Redis.

Fail-soft by design, per Phase 6A's requirement ("If Redis is
unavailable, the application should continue working normally"):
``get_redis_client()`` never raises. If the ``redis`` package isn't
installed, or the server can't be reached, it returns ``None`` and
callers treat that the same as a cache miss / no history / a no-op
invalidation - see cache.py.
"""
import os

_client = None
_attempted = False


def get_redis_client():
    """Return a connected ``redis.Redis`` client, or ``None`` if Redis
    isn't available. Connects at most once per process - the ping
    result is cached, matching the process-wide cache convention used
    for the System Documents in prompt_builder.py.
    """
    global _client, _attempted

    if _attempted:
        return _client

    _attempted = True
    try:
        import redis
    except ImportError:
        _client = None
        return _client

    try:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        _client = client
    except Exception:
        _client = None

    return _client


def reset_redis_client_cache() -> None:
    """Test helper - clears the cached client/connection-attempt flag."""
    global _client, _attempted
    _client = None
    _attempted = False
