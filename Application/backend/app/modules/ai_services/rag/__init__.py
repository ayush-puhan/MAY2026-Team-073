"""ClubConnect AI Assistant - modular RAG package (Phase 4).

Gateway stages 4/6 from Architecture V2 Task 7 ("Determine RAG Context" /
"Retrieve Documents"). This package is intentionally split into small,
single-responsibility modules so each concern (loading, chunking,
embedding, vector search) can be tested and swapped independently -
but it stays a thin orchestration layer, not a framework:

    loader.py             - read .md/.txt (optionally .pdf) files from disk
    chunker.py             - heading-aware Markdown chunking + sliding-window
                              fallback for unheaded text
    embeddings.py           - embedding provider abstraction (ST primary,
                              hash fallback for offline dev/test)
    vector_store.py         - vector store abstraction (FAISS primary,
                              NumPy fallback) with simple persistence
    retriever.py             - top-k similarity search + metadata filtering
    retrieval_service.py     - orchestrates the above end-to-end

``app.modules.ai_services.rag_retriever`` (one level up, sibling to
``intent_router.py``) is the integration layer the rest of the app
imports - it wires this package to the intent catalog's authorization
and ``rag_docs``/role rules. Nothing outside this package should reach
into ``retrieval_service``/``vector_store`` directly.
"""
