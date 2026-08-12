"""Unit tests for app/modules/ai_services/cache.py (Phase 6A).

Per Phase 6A's testing scope: only the new caching functionality is
covered here - Cache MISS, Cache HIT, Cache Expiration, Cache
Invalidation, Conversation Memory, and the Celery cleanup task's
business logic (``cleanup_expired_keys`` - the task wrapper itself,
app/tasks/cache_tasks.py, is a one-line registration around it and
isn't re-tested). SQL Builders, RAG, Prompt Builder, and Auth already
have their own test suites and are untouched here.

Uses a tiny in-memory fake Redis client (not a real Redis server, and
not the ``redis`` package) so these tests are hermetic and don't
require Redis to be running - same spirit as test_sql_context_builder.py
/ test_routes.py's in-memory SQLite fixtures for the DB layer.

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/test_cache.py -q
"""
import time

import pytest

from app.modules.ai_services import cache


class FakeRedis:
    """Minimal in-memory stand-in for the subset of the redis-py API
    cache.py actually uses: get/setex/expire/delete, set ops
    (sadd/smembers/srem/scard/scan_iter/ttl), and list ops
    (lpush/ltrim/lrange).
    """

    def __init__(self):
        self.store = {}  # key -> (value, expire_at | None)
        self.sets = {}  # key -> set()
        self.lists = {}  # key -> list()

    def _drop_if_expired(self, key):
        if key not in self.store:
            return True
        _, expire_at = self.store[key]
        if expire_at is not None and expire_at <= time.time():
            del self.store[key]
            return True
        return False

    def get(self, key):
        if self._drop_if_expired(key):
            return None
        return self.store[key][0]

    def setex(self, key, ttl, value):
        self.store[key] = (value, time.time() + ttl)

    def expire(self, key, ttl):
        if key in self.store:
            value, _ = self.store[key]
            self.store[key] = (value, time.time() + ttl)

    def delete(self, *keys):
        for k in keys:
            self.store.pop(k, None)
            self.sets.pop(k, None)
            self.lists.pop(k, None)

    def sadd(self, key, *values):
        self.sets.setdefault(key, set()).update(values)

    def smembers(self, key):
        return set(self.sets.get(key, set()))

    def srem(self, key, value):
        self.sets.get(key, set()).discard(value)

    def scard(self, key):
        return len(self.sets.get(key, set()))

    def scan_iter(self, match="*"):
        import fnmatch
        for k in list(self.sets.keys()):
            if fnmatch.fnmatch(k, match):
                yield k

    def ttl(self, key):
        if key not in self.store:
            return -2
        _, expire_at = self.store[key]
        if expire_at is None:
            return -1
        remaining = expire_at - time.time()
        if remaining <= 0:
            del self.store[key]
            return -2
        return int(remaining)

    def lpush(self, key, value):
        self.lists.setdefault(key, []).insert(0, value)

    def ltrim(self, key, start, end):
        lst = self.lists.get(key, [])
        self.lists[key] = lst[start : end + 1]

    def lrange(self, key, start, end):
        lst = self.lists.get(key, [])
        return lst[start:] if end == -1 else lst[start : end + 1]


@pytest.fixture()
def fake_redis(monkeypatch):
    client = FakeRedis()
    monkeypatch.setattr(cache, "get_redis_client", lambda: client)
    return client


@pytest.fixture()
def no_redis(monkeypatch):
    monkeypatch.setattr(cache, "get_redis_client", lambda: None)


# --- normalize_prompt / cache-key building ----------------------------------

def test_normalize_prompt_lowercases_trims_and_collapses_whitespace():
    assert cache.normalize_prompt("  What   CLUBS   am I in?\n") == "what clubs am i in?"


def test_normalize_prompt_handles_empty_and_none():
    assert cache.normalize_prompt("") == ""
    assert cache.normalize_prompt(None) == ""


def test_cacheable_intents_matches_policy():
    assert cache.is_cacheable_intent("Membership") is True
    assert cache.is_cacheable_intent("Attendance") is True
    assert cache.is_cacheable_intent("Navigation") is True
    assert cache.is_cacheable_intent("Financial Operations") is False
    assert cache.is_cacheable_intent("Admin Questions") is False
    assert cache.is_cacheable_intent("Rewards") is False


# --- Cache MISS / HIT --------------------------------------------------------

def test_cache_miss_before_anything_is_stored(fake_redis):
    assert cache.get_cached_response(1, "student", "Membership", "what clubs am I in?") is None


def test_cache_hit_after_set(fake_redis):
    cache.set_cached_response(1, "student", "Membership", "What clubs am I in?", "You're in Robotics Club.")
    assert (
        cache.get_cached_response(1, "student", "Membership", "  what CLUBS am i in?  ")
        == "You're in Robotics Club."
    )


def test_cache_scoped_by_user_role_and_intent(fake_redis):
    cache.set_cached_response(1, "student", "Membership", "my clubs", "answer for user 1")
    assert cache.get_cached_response(2, "student", "Membership", "my clubs") is None
    assert cache.get_cached_response(1, "club_president", "Membership", "my clubs") is None
    assert cache.get_cached_response(1, "student", "Navigation", "my clubs") is None


def test_non_cacheable_intent_is_never_stored(fake_redis):
    cache.set_cached_response(1, "student", "Financial Operations", "our budget", "sensitive figures")
    assert cache.get_cached_response(1, "student", "Financial Operations", "our budget") is None


def test_empty_response_is_never_cached(fake_redis):
    cache.set_cached_response(1, "student", "Membership", "my clubs", "")
    assert cache.get_cached_response(1, "student", "Membership", "my clubs") is None


# --- Cache expiration --------------------------------------------------------

def test_cache_entry_expires_after_ttl(fake_redis):
    cache.set_cached_response(1, "student", "Navigation", "where is x", "over there", ttl_seconds=1)
    assert cache.get_cached_response(1, "student", "Navigation", "where is x") == "over there"
    time.sleep(1.2)
    assert cache.get_cached_response(1, "student", "Navigation", "where is x") is None


# --- Cache invalidation -------------------------------------------------------

def test_invalidate_user_cache_clears_only_that_user(fake_redis):
    cache.set_cached_response(1, "student", "Attendance", "my attendance", "5 events")
    cache.set_cached_response(2, "student", "Attendance", "my attendance", "2 events")

    cache.invalidate_user_cache(1)

    assert cache.get_cached_response(1, "student", "Attendance", "my attendance") is None
    assert cache.get_cached_response(2, "student", "Attendance", "my attendance") == "2 events"


def test_invalidate_user_cache_is_a_noop_for_unknown_user(fake_redis):
    cache.invalidate_user_cache(999)  # must not raise


# --- Conversation memory ------------------------------------------------------

def test_conversation_history_empty_for_new_user(fake_redis):
    assert cache.get_conversation_history(1) == []


def test_conversation_history_round_trip_orders_oldest_first(fake_redis):
    cache.append_conversation_turn(1, "hi", "hello!")
    cache.append_conversation_turn(1, "how do I join a club?", "Apply from the club page.")

    history = cache.get_conversation_history(1)

    assert history == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello!"},
        {"role": "user", "content": "how do I join a club?"},
        {"role": "assistant", "content": "Apply from the club page."},
    ]


def test_conversation_history_keeps_only_last_five_exchanges(fake_redis):
    for i in range(7):
        cache.append_conversation_turn(1, f"msg{i}", f"resp{i}")

    history = cache.get_conversation_history(1)

    assert len(history) == 10  # 5 exchanges * (user + assistant)
    assert history[0] == {"role": "user", "content": "msg2"}  # oldest kept
    assert history[-1] == {"role": "assistant", "content": "resp6"}  # newest


def test_conversation_history_is_per_user(fake_redis):
    cache.append_conversation_turn(1, "hi from 1", "reply to 1")
    cache.append_conversation_turn(2, "hi from 2", "reply to 2")

    assert cache.get_conversation_history(1) == [
        {"role": "user", "content": "hi from 1"},
        {"role": "assistant", "content": "reply to 1"},
    ]
    assert cache.get_conversation_history(2) == [
        {"role": "user", "content": "hi from 2"},
        {"role": "assistant", "content": "reply to 2"},
    ]


# --- Celery cleanup task body (cleanup_expired_keys) --------------------------

def test_cleanup_expired_keys_prunes_stale_references_only(fake_redis):
    cache.set_cached_response(1, "student", "Navigation", "q1", "a1", ttl_seconds=1)
    cache.set_cached_response(1, "student", "Attendance", "q2", "a2", ttl_seconds=3600)
    time.sleep(1.2)  # only the Navigation entry expires

    removed = cache.cleanup_expired_keys()

    assert removed == 1
    remaining_keys = fake_redis.smembers(f"aicache:userkeys:1")
    assert len(remaining_keys) == 1
    # the still-valid Attendance entry must still be readable after cleanup
    assert cache.get_cached_response(1, "student", "Attendance", "q2") == "a2"


def test_cleanup_expired_keys_drops_empty_user_sets(fake_redis):
    cache.set_cached_response(1, "student", "Navigation", "q1", "a1", ttl_seconds=1)
    time.sleep(1.2)

    cache.cleanup_expired_keys()

    assert fake_redis.smembers("aicache:userkeys:1") == set()


def test_cleanup_expired_keys_returns_zero_with_nothing_to_clean(fake_redis):
    cache.set_cached_response(1, "student", "Navigation", "q1", "a1", ttl_seconds=3600)
    assert cache.cleanup_expired_keys() == 0


# --- Graceful degradation when Redis is unavailable ---------------------------

def test_everything_is_a_safe_noop_when_redis_is_unavailable(no_redis):
    assert cache.get_cached_response(1, "student", "Membership", "my clubs") is None
    cache.set_cached_response(1, "student", "Membership", "my clubs", "answer")  # must not raise
    assert cache.get_conversation_history(1) == []
    cache.append_conversation_turn(1, "hi", "hello")  # must not raise
    cache.invalidate_user_cache(1)  # must not raise
    assert cache.cleanup_expired_keys() == 0
