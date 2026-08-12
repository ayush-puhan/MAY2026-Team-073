"""Unit tests for app/modules/ai_services/rag/retriever.py (Phase 4).

Note: this is the *generic* retriever unit test file - for the
integration layer (app/modules/ai_services/rag_retriever.py, singular)
see test_rag_retriever_integration.py.
"""
from app.modules.ai_services.rag.embeddings import HashEmbeddingProvider
from app.modules.ai_services.rag.retriever import Retriever
from app.modules.ai_services.rag.vector_store import NumpyVectorStore

CHUNKS = [
    {
        "doc_id": "financial_operations_guide.md",
        "section_title": "Submitting an Expense",
        "text": "submit an expense against a budget for reimbursement",
        "role_filter": ["treasurer", "faculty_advisor"],
    },
    {
        "doc_id": "membership_process_guide.md",
        "section_title": "Applying to Join",
        "text": "how to apply and join a club as a student member",
        "role_filter": ["all"],
    },
    {
        "doc_id": "event_lifecycle_guide.md",
        "section_title": "Registering for Events",
        "text": "register for an upcoming club event",
        "role_filter": ["all"],
    },
]


def _build_retriever():
    provider = HashEmbeddingProvider()
    store = NumpyVectorStore(dimension=provider.dimension)
    vectors = provider.embed([c["text"] for c in CHUNKS])
    store.add(vectors, CHUNKS)
    return Retriever(store, provider)


def test_retrieve_restricts_to_allowed_doc_ids():
    retriever = _build_retriever()

    results = retriever.retrieve(
        "how do I register for an event",
        top_k=3,
        allowed_doc_ids=["event_lifecycle_guide.md"],
        user_roles={"student"},
    )

    assert all(r["doc_id"] == "event_lifecycle_guide.md" for r in results)
    assert len(results) >= 1


def test_retrieve_excludes_restricted_doc_for_disallowed_role():
    retriever = _build_retriever()

    results = retriever.retrieve(
        "submit an expense for reimbursement",
        top_k=3,
        allowed_doc_ids=["financial_operations_guide.md", "membership_process_guide.md"],
        user_roles={"student"},
    )

    assert all(r["doc_id"] != "financial_operations_guide.md" for r in results)


def test_retrieve_includes_restricted_doc_for_allowed_role():
    retriever = _build_retriever()

    results = retriever.retrieve(
        "submit an expense for reimbursement",
        top_k=3,
        allowed_doc_ids=["financial_operations_guide.md"],
        user_roles={"treasurer"},
    )

    assert any(r["doc_id"] == "financial_operations_guide.md" for r in results)


def test_retrieve_empty_query_returns_empty_list():
    retriever = _build_retriever()
    assert retriever.retrieve("   ", top_k=3, allowed_doc_ids=None, user_roles={"student"}) == []


def test_retrieve_result_shape_has_expected_keys():
    retriever = _build_retriever()
    results = retriever.retrieve(
        "join a club",
        top_k=1,
        allowed_doc_ids=["membership_process_guide.md"],
        user_roles={"student"},
    )
    assert set(results[0].keys()) == {"doc_id", "section_title", "text", "score"}
