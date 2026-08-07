"""Unit tests for app/modules/ai_services/rag/embeddings.py (Phase 4).

Exercises the HashEmbeddingProvider directly (deterministic, no
optional dependency needed) and get_default_embedding_provider()'s
fallback behavior. SentenceTransformerEmbeddingProvider itself is not
unit-tested here - it's a thin wrapper around the real library and
downloading the model in CI is out of scope for this phase.
"""
import math

from app.modules.ai_services.rag.embeddings import (
    HASH_EMBEDDING_DIM,
    HashEmbeddingProvider,
    get_default_embedding_provider,
)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_hash_embedding_provider_is_deterministic():
    provider = HashEmbeddingProvider()
    v1 = provider.embed(["submit an expense report"])
    v2 = provider.embed(["submit an expense report"])
    assert v1 == v2


def test_hash_embedding_provider_identical_text_has_similarity_one():
    provider = HashEmbeddingProvider()
    [v1] = provider.embed(["hello world"])
    [v2] = provider.embed(["hello world"])
    assert math.isclose(_dot(v1, v2), 1.0, abs_tol=1e-6)


def test_hash_embedding_provider_different_text_has_lower_similarity():
    provider = HashEmbeddingProvider()
    [v1] = provider.embed(["budget approval treasurer"])
    [v2] = provider.embed(["club membership application"])
    assert _dot(v1, v2) < 0.5


def test_hash_embedding_provider_vectors_are_normalized():
    provider = HashEmbeddingProvider()
    [v] = provider.embed(["some arbitrary sentence to embed"])
    norm = math.sqrt(sum(x * x for x in v))
    assert math.isclose(norm, 1.0, abs_tol=1e-6)


def test_hash_embedding_provider_respects_custom_dimension():
    provider = HashEmbeddingProvider(dimension=64)
    [v] = provider.embed(["text"])
    assert len(v) == 64


def test_default_dimension_constant():
    provider = HashEmbeddingProvider()
    assert provider.dimension == HASH_EMBEDDING_DIM


def test_get_default_embedding_provider_returns_a_usable_provider():
    # sentence-transformers isn't installed in this environment, so this
    # exercises the fallback path - but the assertion holds either way.
    provider = get_default_embedding_provider()
    assert provider.name in ("sentence-transformers", "hash-fallback")
    [vector] = provider.embed(["test"])
    assert len(vector) == provider.dimension
