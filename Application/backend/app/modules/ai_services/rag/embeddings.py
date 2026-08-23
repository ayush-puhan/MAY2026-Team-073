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


class GoogleGenAIEmbeddingProvider:
    """Zero-RAM semantic embedding using the Gemini API.
    Perfect for Render Free Tier to avoid PyTorch OOM crashes.
    """

    name = "google-genai"

    def __init__(self, model_name: str = "models/text-embedding-004"):
        import google.generativeai as genai
        import os
        
        self.model_name = model_name
        self.dimension = 768
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    def embed(self, texts: "list[str]") -> "list[list[float]]":
        import google.generativeai as genai
        result = genai.embed_content(
            model=self.model_name,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']


def get_default_embedding_provider() -> EmbeddingProvider:
    """Use Gemini Embeddings for Zero-RAM, high-quality RAG on Render."""
    try:
        import google.generativeai
        import os
        if os.environ.get("GEMINI_API_KEY"):
            return GoogleGenAIEmbeddingProvider()
    except ImportError:
        pass
        
    try:
        # Avoid loading PyTorch on Render Free Tier
        if not os.environ.get("RENDER"):
            return SentenceTransformerEmbeddingProvider()
    except Exception:
        pass
        
    return HashEmbeddingProvider()
