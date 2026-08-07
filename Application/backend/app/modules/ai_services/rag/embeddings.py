"""Embedding Layer.

A minimal provider abstraction so the rest of the RAG package never
imports ``sentence_transformers`` (or anything else) directly - it just
asks for "the configured embedding provider". Two providers:

    SentenceTransformerEmbeddingProvider - the real, primary provider
        (``all-MiniLM-L6-v2``, per NEXT_PHASE.md). Requires the optional
        ``sentence-transformers`` dependency.
    HashEmbeddingProvider - a deterministic, dependency-free fallback so
        local dev/CI can run this package's tests (and the app can still
        answer, in a degraded-relevance way) without downloading a model.
        Not a second production-grade provider - it exists purely to keep
        this package importable and testable without the heavy dependency.

``get_default_embedding_provider()`` picks Sentence-Transformers when
available and silently falls back to the hash provider otherwise -
callers that care which one is active can check the returned provider's
``name``.
"""
import hashlib
import math
from typing import Protocol

MODEL_NAME = "all-MiniLM-L6-v2"
HASH_EMBEDDING_DIM = 256


class EmbeddingProvider(Protocol):
    name: str
    dimension: int

    def embed(self, texts: "list[str]") -> "list[list[float]]":
        ...


class SentenceTransformerEmbeddingProvider:
    """Primary embedding provider - real semantic embeddings."""

    name = "sentence-transformers"

    def __init__(self, model_name: str = MODEL_NAME):
        from sentence_transformers import SentenceTransformer  # optional dep

        self._model = SentenceTransformer(model_name)
        self.dimension = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: "list[str]") -> "list[list[float]]":
        vectors = self._model.encode(list(texts), convert_to_numpy=True, normalize_embeddings=True)
        return vectors.tolist()


class HashEmbeddingProvider:
    """Dependency-free fallback: deterministic hashed bag-of-words vectors.

    Not semantically meaningful in the way a trained model is, but
    deterministic, fast, and requires nothing beyond the standard
    library - keeps this package testable and the app functional when
    ``sentence-transformers`` isn't installed.
    """

    name = "hash-fallback"

    def __init__(self, dimension: int = HASH_EMBEDDING_DIM):
        self.dimension = dimension

    def _embed_one(self, text: str) -> "list[float]":
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed(self, texts: "list[str]") -> "list[list[float]]":
        return [self._embed_one(t) for t in texts]


def get_default_embedding_provider() -> EmbeddingProvider:
    """Sentence-Transformers if installed and loadable, else the hash fallback."""
    try:
        return SentenceTransformerEmbeddingProvider()
    except Exception:
        return HashEmbeddingProvider()
