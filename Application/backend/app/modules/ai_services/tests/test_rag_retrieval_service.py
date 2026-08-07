"""Unit tests for app/modules/ai_services/rag/retrieval_service.py (Phase 4).

Uses a temporary knowledge-base directory (not the real
knowledge_base/rag/) so these tests don't depend on the actual
documents' content - only on the orchestration logic (load -> chunk ->
embed once -> search -> filter).
"""
from app.modules.ai_services.rag.retrieval_service import (
    RetrievalService,
    get_retrieval_service,
    reset_retrieval_service_cache,
)


def _write_kb(tmp_path):
    (tmp_path / "membership_process_guide.md").write_text(
        "# Membership Process Guide\n\n"
        "## Applying to Join\n\n"
        "A student applies to join a club through the platform.\n"
    )
    (tmp_path / "financial_operations_guide.md").write_text(
        "# Financial Operations Guide\n\n"
        "## Submitting an Expense\n\n"
        "A treasurer submits an expense claim against a club budget.\n"
    )
    return str(tmp_path)


def test_retrieval_service_builds_index_lazily(tmp_path):
    kb_dir = _write_kb(tmp_path)
    service = RetrievalService(kb_dir)

    assert service._built is False
    service.retrieve("how do I join a club")
    assert service._built is True


def test_retrieval_service_embeds_corpus_only_once(tmp_path):
    kb_dir = _write_kb(tmp_path)
    service = RetrievalService(kb_dir)

    service.retrieve("join a club")
    service.retrieve("submit an expense")
    service.retrieve("another query")

    # ensure_built only calls _build_index once regardless of query count
    assert service._built is True
    first_store = service._vector_store
    service.retrieve("yet another query")
    assert service._vector_store is first_store


def test_retrieval_service_applies_role_filter_map(tmp_path):
    kb_dir = _write_kb(tmp_path)
    service = RetrievalService(
        kb_dir,
        role_filter_map={"financial_operations_guide.md": ["treasurer"]},
    )

    student_results = service.retrieve(
        "submit an expense",
        allowed_doc_ids=["financial_operations_guide.md"],
        user_roles={"student"},
    )
    treasurer_results = service.retrieve(
        "submit an expense",
        allowed_doc_ids=["financial_operations_guide.md"],
        user_roles={"treasurer"},
    )

    assert student_results == []
    assert len(treasurer_results) >= 1


def test_retrieval_service_restricts_to_allowed_doc_ids(tmp_path):
    kb_dir = _write_kb(tmp_path)
    service = RetrievalService(kb_dir)

    # Even a query worded like the financial doc's content should never
    # surface it once allowed_doc_ids excludes it - top-k still returns
    # the best-available match *within* the allowed set, never a chunk
    # from outside it.
    results = service.retrieve(
        "submit an expense",
        allowed_doc_ids=["membership_process_guide.md"],
        user_roles={"student"},
    )

    assert all(r["doc_id"] == "membership_process_guide.md" for r in results)
    assert not any(r["doc_id"] == "financial_operations_guide.md" for r in results)


def test_retrieval_service_empty_knowledge_base_dir_returns_empty(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    service = RetrievalService(str(empty_dir))

    assert service.retrieve("anything") == []


def test_retrieval_service_persistence_roundtrip(tmp_path):
    kb_dir = _write_kb(tmp_path)
    service = RetrievalService(kb_dir)
    service.retrieve("join a club")  # forces build

    index_path = str(tmp_path / "index" / "kb")
    service.save(index_path)

    reloaded = RetrievalService(kb_dir)
    loaded = reloaded.load(index_path)

    assert loaded is True
    results = reloaded.retrieve(
        "join a club", allowed_doc_ids=["membership_process_guide.md"], user_roles={"student"}
    )
    assert len(results) >= 1


def test_get_retrieval_service_returns_same_instance_for_same_dir(tmp_path):
    reset_retrieval_service_cache()
    kb_dir = _write_kb(tmp_path)

    service_a = get_retrieval_service(kb_dir)
    service_b = get_retrieval_service(kb_dir)

    assert service_a is service_b
    reset_retrieval_service_cache()
