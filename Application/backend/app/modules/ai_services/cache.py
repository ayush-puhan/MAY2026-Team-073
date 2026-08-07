"""ClubConnect AI Assistant - Response Cache + Conversation Memory (Phase 6A).

Scope (see NEXT_PHASE.md's Phase 6A entry / CHANGELOG.md): a lightweight
Redis-backed cache in front of the Gemini call in routes.py, plus a
short (last-5-exchange) conversation history passed to the existing
Prompt Builder. This module owns all of that logic so routes.py only
needs a handful of call sites - see routes.py's ``chat()``.

Fail-soft, always: every function here degrades to a no-op/empty
result when Redis isn't reachable (app/core/redis.py's
``get_redis_client()`` returns ``None`` in that case) rather than
raising - the rest of the platform, including the AI chat endpoint,
must keep working exactly as before with no cache at all.
"""
import hashlib
import json
import os
import re

from app.core.redis import get_redis_client

# --- Key namespaces ---------------------------------------------------------

_CACHE_PREFIX = "aicache:resp:"
_USER_KEYS_PREFIX = "aicache:userkeys:"
_HISTORY_PREFIX = "aicache:history:"

_DEFAULT_TTL_SECONDS = int(os.environ.get("AI_CACHE_TTL_SECONDS", 3600))
_HISTORY_TTL_SECONDS = int(os.environ.get("AI_CACHE_HISTORY_TTL_SECONDS", 86400))

# "Store only the last five conversation exchanges" (Phase 6A spec) - one
# exchange = one user message + the assistant's reply to it.
_HISTORY_MAX_EXCHANGES = 5

# --- Cache policy ------------------------------------------------------------
#
# Only intents whose answer is deterministic for a given user+message at
# a point in time are cached - matches the Phase 6A cache-policy list
# verbatim (Membership, Profile, Attendance, Navigation, FAQs, Role
# Questions, Club Recommendation, Event Recommendation, General Help),
# mapped onto this project's actual intent_router.py catalog names:
#
#   Membership            -> "Membership"
#   FAQs / General Help   -> "Getting Started", "Membership Process",
#                            "Event Registration" (all three are static
#                            process/orientation explanations, not
#                            personalized live data)
#   Role Questions         -> "Role Capabilities Q&A"
#   Profile                -> "Profile & Account"
#   Attendance              -> "Attendance"
#   Navigation              -> "Navigation"
#   Club Recommendation     -> "Club Recommendation"
#   Event Recommendation    -> "Event Recommendation"
#
# Deliberately excluded (frequently-changing / operational, per the
# cache-policy "Do NOT cache" list): Financial Operations, Admin
# Questions, Faculty Questions, Application Status, Support Tickets,
# Rewards, Announcements, Club Creation & Governance, Club Discovery,
# Emergency Reporting, Ambiguous Request, Out-of-Scope.
CACHEABLE_INTENTS = frozenset({
    "Membership",
    "Getting Started",
    "Membership Process",
    "Event Registration",
    "Role Capabilities Q&A",
    "Profile & Account",
    "Attendance",
    "Navigation",
    "Club Recommendation",
    "Event Recommendation",
})


def is_cacheable_intent(intent_name: str) -> bool:
    return intent_name in CACHEABLE_INTENTS


def normalize_prompt(message: str) -> str:
    """Lowercase, trim, and collapse repeated whitespace - nothing more
    complicated than that, per the Phase 6A cache spec."""
    return re.sub(r"\s+", " ", (message or "").strip().lower())


def _build_cache_key(user_id, role, intent_name: str, message: str) -> str:
    """Cache key is based on user_id + role + intent + normalized_prompt
    (never a JWT token, per the Phase 6A cache spec)."""
    normalized = normalize_prompt(message)
    raw = f"{user_id}:{role}:{intent_name}:{normalized}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{_CACHE_PREFIX}{digest}"


def get_cached_response(user_id, role, intent_name: str, message: str) -> "str | None":
    """Return the cached Gemini response text for this exact
    user/role/intent/prompt, or ``None`` on a cache miss, a
    non-cacheable intent, or if Redis is unavailable.
    """
    if not is_cacheable_intent(intent_name):
        return None

    client = get_redis_client()
    if client is None:
        return None

    key = _build_cache_key(user_id, role, intent_name, message)
    try:
        return client.get(key)
    except Exception:
        return None


def set_cached_response(
    user_id, role, intent_name: str, message: str, response_text: str, ttl_seconds: "int | None" = None
) -> None:
    """Cache a successful Gemini response. No-op for non-cacheable
    intents, empty responses, or when Redis is unavailable - failed
    responses must never be cached (routes.py only calls this after a
    successful ``generate_response()`` call).
    """
    if not response_text or not is_cacheable_intent(intent_name):
        return

    client = get_redis_client()
    if client is None:
        return

    key = _build_cache_key(user_id, role, intent_name, message)
    ttl = ttl_seconds or _DEFAULT_TTL_SECONDS
    try:
        client.setex(key, ttl, response_text)
        # Track this key against the user so invalidate_user_cache() can
        # remove exactly this user's entries without a full cache flush.
        user_set_key = f"{_USER_KEYS_PREFIX}{user_id}"
        client.sadd(user_set_key, key)
        client.expire(user_set_key, ttl)
    except Exception:
        pass


def invalidate_user_cache(user_id) -> None:
    """Remove only this user's cached AI responses. Called when a
    user's profile information changes - never flushes the whole
    Redis cache.
    """
    client = get_redis_client()
    if client is None:
        return

    user_set_key = f"{_USER_KEYS_PREFIX}{user_id}"
    try:
        keys = client.smembers(user_set_key)
        if keys:
            client.delete(*keys)
        client.delete(user_set_key)
    except Exception:
        pass


def cleanup_expired_keys() -> int:
    """Prune references to already-expired cache entries from the
    per-user key-tracking sets used by ``invalidate_user_cache()``.

    Redis already expires the cache entries themselves via TTL with no
    help needed here - this only keeps the tracking sets from growing
    unbounded with pointers to entries that expired on their own. This
    is the body of the Celery cleanup task (app/tasks/cache_tasks.py);
    kept as a plain function so it's testable without a running worker.
    """
    client = get_redis_client()
    if client is None:
        return 0

    removed = 0
    try:
        for user_set_key in client.scan_iter(match=f"{_USER_KEYS_PREFIX}*"):
            for member in client.smembers(user_set_key):
                if client.ttl(member) == -2:  # -2 = key doesn't exist / expired
                    client.srem(user_set_key, member)
                    removed += 1
            if client.scard(user_set_key) == 0:
                client.delete(user_set_key)
    except Exception:
        return removed
    return removed


# --- Conversation memory (last 5 exchanges) ---------------------------------

def _history_key(user_id) -> str:
    return f"{_HISTORY_PREFIX}{user_id}"


def append_conversation_turn(user_id, message: str, response_text: str) -> None:
    """Append one exchange (user message + assistant response) to this
    user's short conversation history and trim to the last 5
    exchanges. A Redis List is sufficient, per the Phase 6A spec - no
    advanced memory system.
    """
    client = get_redis_client()
    if client is None:
        return

    key = _history_key(user_id)
    exchange = json.dumps({"user": message, "assistant": response_text})
    try:
        client.lpush(key, exchange)
        client.ltrim(key, 0, _HISTORY_MAX_EXCHANGES - 1)
        client.expire(key, _HISTORY_TTL_SECONDS)
    except Exception:
        pass


def get_conversation_history(user_id) -> list:
    """Return up to the last 5 exchanges, oldest first, as
    ``[{"role": "user"/"assistant", "content": str}, ...]`` - the exact
    shape ``prompt_builder.build_prompt()``'s ``history`` argument
    already expects, so no changes were needed there. Returns ``[]``
    when there's no history yet or Redis is unavailable.
    """
    client = get_redis_client()
    if client is None:
        return []

    key = _history_key(user_id)
    try:
        raw_exchanges = client.lrange(key, 0, -1)  # newest-first
    except Exception:
        return []

    exchanges = []
    for raw in raw_exchanges:
        try:
            exchanges.append(json.loads(raw))
        except (TypeError, ValueError):
            continue
    exchanges.reverse()  # oldest first

    turns = []
    for exchange in exchanges:
        turns.append({"role": "user", "content": exchange.get("user", "")})
        turns.append({"role": "assistant", "content": exchange.get("assistant", "")})
    return turns
