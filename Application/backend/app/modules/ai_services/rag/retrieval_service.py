"""Retrieval Service.

The single orchestration layer for the RAG package:

    query -> embedding -> vector search -> chunks

Everything upstream of this (loader/chunker/embeddings/vector_store) is
wired together here exactly once per process: the corpus is loaded,
chunked, and embedded on first use and kept in memory - never
re-embedded per request (per NEXT_PHASE.md). Only the caller's live
query gets embedded at request time.

``role_filter_map`` lets the caller mark specific documents as
restricted (e.g. ``{"financial_operations_guide.md": ["treasurer",
"faculty_advisor"]}``); anything not listed defaults to ``["all"]``.
This module does not decide *who* gets which role - that's
rag_retriever.py's job, using the existing intent/authorization catalog.
"""
import os

from .chunker import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, chunk_documents
from .embeddings import get_default_embedding_provider
from .loader import load_documents
from .retriever import Retriever
from .vector_store import get_default_vector_store

DEFAULT_ROLE_FILTER = ["all"]


class RetrievalService:
    def __init__(
        self,
        knowledge_base_dir: str,
        role_filter_map: "dict[str, list[str]] | None" = None,
        embedding_provider=None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ):
        self.knowledge_base_dir = knowledge_base_dir
        self.role_filter_map = role_filter_map or {}
        self.chunk_size = chunk_size
        self.overlap = overlap

        self._embedding_provider = embedding_provider or get_default_embedding_provider()
        self._vector_store = None
        self._retriever = None
        self._built = False

    # -- index construction (lazy: happens once, on first retrieve()) ----

    def _build_index(self) -> None:
        documents = load_documents(self.knowledge_base_dir)
        chunks = chunk_documents(documents, self.chunk_size, self.overlap)

        self._vector_store = get_default_vector_store(self._embedding_provider.dimension)
        self._retriever = Retriever(self._vector_store, self._embedding_provider)

        if not chunks:
            self._built = True
            return

        texts = [c.text for c in chunks]
        vectors = self._embedding_provider.embed(texts)
        metadatas = [
            {
                "doc_id": c.doc_id,
                "section_title": c.section_title,
                "text": c.text,
                "role_filter": self.role_filter_map.get(c.doc_id, DEFAULT_ROLE_FILTER),
            }
            for c in chunks
        ]
        self._vector_store.add(vectors, metadatas)
        self._built = True

    def ensure_built(self) -> None:
        if not self._built:
            self._build_index()

    # -- persistence (optional - rebuilding from the small Markdown
    # corpus is cheap, but this lets a deployment skip re-embedding on
    # every process restart if it chooses to) ---------------------------

    def save(self, index_path: str) -> None:
        self.ensure_built()
        self._vector_store.save(index_path)

    def load(self, index_path: str) -> bool:
        """Load a previously-saved index. Returns False (and leaves the
        service unbuilt) if no index exists at that path yet."""
        if not (os.path.exists(index_path + ".faiss") or os.path.exists(index_path + ".npy")):
            return False

        self._vector_store = get_default_vector_store(self._embedding_provider.dimension)
        self._vector_store.load(index_path)
        self._retriever = Retriever(self._vector_store, self._embedding_provider)
        self._built = True
        return True

    # -- retrieval ---------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3, allowed_doc_ids=None, user_roles=None) -> "list[dict]":
        self.ensure_built()
        return self._retriever.retrieve(query, top_k=top_k, allowed_doc_ids=allowed_doc_ids, user_roles=user_roles)


# ---------------------------------------------------------------------------
# Process-wide singleton so the corpus is embedded once, not per request.
# ---------------------------------------------------------------------------

_service_cache: "dict[tuple, RetrievalService]" = {}


def get_retrieval_service(knowledge_base_dir: str, role_filter_map=None) -> RetrievalService:
    key = (knowledge_base_dir,)
    if key not in _service_cache:
        _service_cache[key] = RetrievalService(knowledge_base_dir, role_filter_map=role_filter_map)
    return _service_cache[key]


def reset_retrieval_service_cache() -> None:
    """Test helper - clears the process-wide singleton cache."""
    _service_cache.clear()
