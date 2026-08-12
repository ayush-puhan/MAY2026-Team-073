"""Retriever.

Top-k semantic retrieval over a vector store, with metadata filtering
applied *before* results are handed back - never search-then-hope: a
chunk that doesn't pass the doc_id/role filter is never returned, no
matter how high its similarity score.

Chunk metadata is expected to carry (see retrieval_service.py):
    doc_id: str            - source filename
    section_title: str
    text: str
    role_filter: list[str] - ["all"] or a specific set like
                              ["treasurer", "faculty"]

Because the underlying stores here don't support native pre-filtered
search, filtering is done by over-fetching (``top_k * OVERSAMPLE``)
candidates and then filtering down - fine at this corpus's scale (a
handful of documents, low tens of chunks total).
"""

OVERSAMPLE_FACTOR = 5


def _role_allowed(chunk_role_filter, user_roles) -> bool:
    if not chunk_role_filter or "all" in chunk_role_filter:
        return True
    if not user_roles:
        return False
    return any(role in chunk_role_filter for role in user_roles)


class Retriever:
    def __init__(self, vector_store, embedding_provider):
        self._vector_store = vector_store
        self._embedding_provider = embedding_provider

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        allowed_doc_ids=None,
        user_roles=None,
    ) -> "list[dict]":
        """Return up to ``top_k`` chunks matching the query and filters.

        allowed_doc_ids: iterable of filenames to restrict the candidate
            set to (e.g. the current intent's ``rag_docs``). None means
            "no doc_id restriction" - callers should always pass this
            explicitly in practice (see rag_retriever.py); it's optional
            here only so the Retriever stays independently testable.
        user_roles: iterable of role strings the requesting user holds
            (platform role + club roles), checked against each chunk's
            ``role_filter``.
        """
        if not query or not query.strip():
            return []

        allowed_doc_ids = set(allowed_doc_ids) if allowed_doc_ids is not None else None
        user_roles = set(user_roles) if user_roles else set()

        [query_vector] = self._embedding_provider.embed([query])

        fetch_k = max(top_k * OVERSAMPLE_FACTOR, top_k)
        candidates = self._vector_store.search(query_vector, fetch_k)

        results = []
        for metadata, score in candidates:
            if allowed_doc_ids is not None and metadata.get("doc_id") not in allowed_doc_ids:
                continue
            if not _role_allowed(metadata.get("role_filter"), user_roles):
                continue
            results.append({
                "doc_id": metadata.get("doc_id"),
                "section_title": metadata.get("section_title"),
                "text": metadata.get("text"),
                "score": score,
            })
            if len(results) >= top_k:
                break

        return results
