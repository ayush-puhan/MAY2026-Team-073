"""Unit tests for app/modules/ai_services/rag/vector_store.py (Phase 4).

Exercises NumpyVectorStore directly (dependency-free) and
get_default_vector_store()'s fallback behavior. FaissVectorStore itself
is not unit-tested here since faiss-cpu isn't installed in this
environment - it's a thin wrapper the same shape as the Numpy backend.
"""
from app.modules.ai_services.rag.vector_store import (
    NumpyVectorStore,
    get_default_vector_store,
)

VECTORS = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.9, 0.1, 0.0],
]
METADATAS = [
    {"doc_id": "a.md", "section_title": "A", "text": "a text"},
    {"doc_id": "b.md", "section_title": "B", "text": "b text"},
    {"doc_id": "a.md", "section_title": "A2", "text": "a2 text"},
]


def test_numpy_vector_store_returns_most_similar_first():
    store = NumpyVectorStore(dimension=3)
    store.add(VECTORS, METADATAS)

    results = store.search([1.0, 0.0, 0.0], top_k=3)

    assert results[0][0]["doc_id"] == "a.md"
    assert results[0][0]["section_title"] == "A"


def test_numpy_vector_store_respects_top_k():
    store = NumpyVectorStore(dimension=3)
    store.add(VECTORS, METADATAS)

    results = store.search([1.0, 0.0, 0.0], top_k=1)

    assert len(results) == 1


def test_numpy_vector_store_len_tracks_added_vectors():
    store = NumpyVectorStore(dimension=3)
    assert len(store) == 0
    store.add(VECTORS, METADATAS)
    assert len(store) == 3


def test_numpy_vector_store_empty_search_returns_empty_list():
    store = NumpyVectorStore(dimension=3)
    assert store.search([1.0, 0.0, 0.0], top_k=3) == []


def test_numpy_vector_store_persistence_roundtrip(tmp_path):
    store = NumpyVectorStore(dimension=3)
    store.add(VECTORS, METADATAS)
    index_path = str(tmp_path / "index")
    store.save(index_path)

    reloaded = NumpyVectorStore(dimension=3)
    reloaded.load(index_path)

    assert len(reloaded) == len(store)
    results = reloaded.search([1.0, 0.0, 0.0], top_k=1)
    assert results[0][0]["doc_id"] == "a.md"


def test_get_default_vector_store_returns_a_usable_store():
    # faiss-cpu isn't installed in this environment, so this exercises
    # the fallback path - but the assertion holds either way.
    store = get_default_vector_store(dimension=3)
    assert store.name in ("faiss", "numpy-fallback")
    store.add(VECTORS, METADATAS)
    assert len(store) == 3
