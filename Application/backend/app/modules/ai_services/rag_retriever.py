"""ClubConnect AI Assistant - RAG Retriever (Phase 4).

Gateway stages 4/6 from Architecture V2 Task 7 ("Determine RAG Context" /
"Retrieve Documents"). This is the integration layer between the
modular ``rag/`` package (loader/chunker/embeddings/vector_store/
retriever/retrieval_service) and the existing Intent Router
(``intent_router.py``): it is the only thing ``routes.py`` should ever
import from this phase's work.

Security (per project convention - authorization happens BEFORE
retrieval, never after):
    - ``routes.py`` only calls ``retrieve_rag_context`` once
      ``authorize_intent()`` has already returned True for the request.
    - This function *additionally* restricts the candidate document set
      to the given intent's ``rag_docs`` and to chunks whose
      ``role_filter`` the caller's role(s) satisfy - so even a
      programming mistake elsewhere (e.g. calling this for an
      unauthorized intent) can't leak the Financial Operations guide to
      a plain student. Nothing here relies on the LLM to hide
      confidential content - restricted chunks are simply never in the
      candidate set that reaches it.
    - Intents with no ``rag_docs`` (SQL-only intents) return ``[]``
      immediately, without ever touching the retrieval service - the
      embedding model is never invoked for those.

Future caching (Phase 5, not implemented here): the natural cache key
for this function's result is
``(user_id, effective_role, intent_name, normalized_query)`` - the
signature below already carries everything that key needs.
"""
import os

from flask import current_app

from app.modules.ai_services.intent_router import INTENT_CATALOG
from app.modules.ai_services.rag.retrieval_service import get_retrieval_service

DEFAULT_TOP_K = 3

# Only the Financial Operations guide is role-restricted (per
# intent_router.py's "Financial Operations" intent definition and
# assistant_conversation_behavior.md §8). Everything else defaults to
# ["all"] in retrieval_service.py.
ROLE_FILTER_MAP = {
    "financial_operations_guide.md": ["faculty_advisor", "treasurer"],
}

_DEFAULT_KB_RAG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "knowledge_base", "rag"
)


def _resolve_kb_rag_dir() -> str:
    """The 'rag' subdirectory of the configured KNOWLEDGE_BASE_DIR.

    Falls back to this module's own knowledge_base/rag path when called
    outside a Flask app context (e.g. some unit tests), matching
    config.py's own default.
    """
    try:
        base = current_app.config.get("KNOWLEDGE_BASE_DIR")
    except RuntimeError:
        base = None

    return os.path.join(base, "rag") if base else _DEFAULT_KB_RAG_DIR


def _role_value(role):
    return role.value if hasattr(role, "value") else role


def _normalize_roles(user_role, club_roles) -> set:
    roles = set()
    if user_role is not None:
        roles.add(_role_value(user_role))
    for r in club_roles:
        roles.add(_role_value(r))
    return roles


def retrieve_rag_context(intent_name: str, message: str, user_role, club_roles=(), top_k: int = DEFAULT_TOP_K) -> "list[dict]":
    """Retrieve up to ``top_k`` RAG chunks relevant to ``message`` for the
    given intent, restricted to that intent's documents and the caller's
    role(s).

    Returns ``[]`` for any intent with no ``rag_docs`` (SQL-only intents)
    - without ever calling the embedding model - and for an unknown
    intent name (fail closed, matching ``authorize_intent``'s stance).
    """
    intent = INTENT_CATALOG.get(intent_name)
    if intent is None or not intent.rag_docs:
        return []

    if not message or not message.strip():
        return []

    service = get_retrieval_service(_resolve_kb_rag_dir(), role_filter_map=ROLE_FILTER_MAP)
    user_roles = _normalize_roles(user_role, club_roles)

    chunks = service.retrieve(
        message,
        top_k=top_k,
        allowed_doc_ids=intent.rag_docs,
        user_roles=user_roles,
    )

    return [
        {"doc_id": c["doc_id"], "section_title": c["section_title"], "text": c["text"]}
        for c in chunks
    ]
