"""Unit tests for app/modules/ai_services/rag_retriever.py (Phase 4).

This is the integration layer that wires the modular rag/ package to
the existing Intent Router. Runs against the real
knowledge_base/rag/ documents copied at Phase 1 (same corpus the app
serves in production), via app.config.KNOWLEDGE_BASE_DIR.

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q
"""
import pytest

from app.database.enums import ClubMemberRole, UserRole
from app.modules.ai_services.rag.retrieval_service import reset_retrieval_service_cache
from app.modules.ai_services.rag_retriever import retrieve_rag_context


@pytest.fixture(autouse=True)
def _clear_retrieval_cache():
    # Each test may exercise a different flask app-context KNOWLEDGE_BASE_DIR
    # (or none), so never let one test's built index leak into another.
    reset_retrieval_service_cache()
    yield
    reset_retrieval_service_cache()


def test_sql_only_intent_returns_empty_list_without_touching_retrieval(monkeypatch):
    """'Club Discovery' has rag_docs=() - must return [] and must never
    construct a retrieval service (i.e. never call the embedding model)."""
    import app.modules.ai_services.rag_retriever as rag_retriever_module

    def _explode(*args, **kwargs):
        raise AssertionError("retrieval service must not be built for a SQL-only intent")

    monkeypatch.setattr(rag_retriever_module, "get_retrieval_service", _explode)

    result = retrieve_rag_context("Club Discovery", "find a club for me", UserRole.STUDENT, [])

    assert result == []


def test_unknown_intent_fails_closed():
    assert retrieve_rag_context("Not A Real Intent", "hello", UserRole.STUDENT, []) == []


def test_empty_message_returns_empty_list():
    assert retrieve_rag_context("Membership Process", "   ", UserRole.STUDENT, []) == []


def test_membership_query_never_surfaces_rewards_content():
    """A Membership Process query must only ever retrieve from that
    intent's own rag_docs - never another intent's document."""
    results = retrieve_rag_context(
        "Membership Process", "how do I apply to join a club", UserRole.STUDENT, []
    )

    assert results, "expected at least one chunk for a real query against a real doc"
    assert all(r["doc_id"] == "membership_process_guide.md" for r in results)


def test_financial_operations_excluded_for_plain_student():
    results = retrieve_rag_context(
        "Financial Operations", "how do I submit an expense for reimbursement",
        UserRole.STUDENT, [],
    )

    assert results == []


def test_financial_operations_included_for_treasurer_club_role():
    results = retrieve_rag_context(
        "Financial Operations", "how do I submit an expense for reimbursement",
        UserRole.STUDENT, [ClubMemberRole.TREASURER],
    )

    assert results
    assert all(r["doc_id"] == "financial_operations_guide.md" for r in results)


def test_financial_operations_included_for_faculty_advisor_platform_role():
    results = retrieve_rag_context(
        "Financial Operations", "how do I submit an expense for reimbursement",
        UserRole.FACULTY_ADVISOR, [],
    )

    assert results
    assert all(r["doc_id"] == "financial_operations_guide.md" for r in results)


def test_result_chunk_shape():
    results = retrieve_rag_context(
        "Membership Process", "how do I apply to join a club", UserRole.STUDENT, []
    )

    assert results
    assert set(results[0].keys()) == {"doc_id", "section_title", "text"}


# ---------------------------------------------------------------------------
# role_permissions_reference.md (Phase 6 final polish - RAG task)
#
# Confirms the new document isn't just an eligible candidate (that's
# covered by test_intent_router.py's rag_docs assertion) but is
# actually surfaced by real retrieval against the live corpus for the
# exact role-capability questions called out for this document.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("message", [
    "What can a Secretary do?",
    "What can a Treasurer do?",
    "Difference between President and Vice President",
    "Can a Student approve budgets?",
    "Who approves club creation?",
    "Who can manage expenses?",
    "What permissions does a Faculty Advisor have?",
])
def test_role_permissions_reference_is_actually_retrieved(message):
    results = retrieve_rag_context("Role Capabilities Q&A", message, UserRole.STUDENT, [])

    assert results, "expected at least one chunk for a real role-capability query"
    doc_ids = {r["doc_id"] for r in results}
    assert "role_permissions_reference.md" in doc_ids


def test_role_permissions_reference_available_to_any_authenticated_role():
    """Unlike financial_operations_guide.md, this document is not
    role-filtered - any authenticated role may ask a role-capability
    question about any role (e.g. a student asking what a treasurer
    can do), so it must not be restricted via ROLE_FILTER_MAP."""
    from app.modules.ai_services.rag_retriever import ROLE_FILTER_MAP

    assert "role_permissions_reference.md" not in ROLE_FILTER_MAP

    results = retrieve_rag_context(
        "Role Capabilities Q&A", "What can a Treasurer do?", UserRole.STUDENT, []
    )
    assert any(r["doc_id"] == "role_permissions_reference.md" for r in results)
