"""Unit tests for app/modules/ai_services/rag/chunker.py (Phase 4)."""
from app.modules.ai_services.rag.chunker import chunk_document

MULTI_HEADING_DOC = """# Financial Operations Guide

## Purpose

Explains how club-level financial operations work.

## Overview

Club finances are organized around budgets.

## Definitions

Budget and expense definitions live here.
"""


def test_chunk_document_splits_on_headings():
    chunks = chunk_document("financial_operations_guide.md", MULTI_HEADING_DOC)

    # The lone top-level "# Financial Operations Guide" title heading has
    # no body text of its own before the next heading, so it correctly
    # produces no chunk - only headings with actual content do.
    titles = [c.section_title for c in chunks]
    assert titles == ["Purpose", "Overview", "Definitions"]
    assert all(c.doc_id == "financial_operations_guide.md" for c in chunks)


def test_chunk_document_section_bodies_do_not_leak_into_each_other():
    chunks = chunk_document("doc.md", MULTI_HEADING_DOC)

    purpose_chunk = next(c for c in chunks if c.section_title == "Purpose")
    overview_chunk = next(c for c in chunks if c.section_title == "Overview")

    assert "financial operations work" in purpose_chunk.text
    assert "budgets" in overview_chunk.text
    assert "budgets" not in purpose_chunk.text


def test_chunk_document_no_headings_falls_back_to_single_chunk_when_small():
    text = "Just a short paragraph with no headings at all."
    chunks = chunk_document("plain.txt", text)

    assert len(chunks) == 1
    assert chunks[0].section_title == ""
    assert chunks[0].text == text


def test_chunk_document_sliding_window_for_oversized_section():
    long_body = " ".join(f"word{i}" for i in range(1000))
    text = f"# Big Section\n\n{long_body}"

    chunks = chunk_document("big.md", text, chunk_size=200, overlap=20)

    assert len(chunks) > 1
    assert all(c.section_title == "Big Section" for c in chunks)
    # Chunk sizes stay within target (allowing the sliding window's own size).
    assert all(len(c.text.split()) <= 200 for c in chunks)


def test_chunk_document_overlap_shares_words_between_consecutive_chunks():
    long_body = " ".join(f"word{i}" for i in range(500))
    text = f"# Section\n\n{long_body}"

    chunks = chunk_document("doc.md", text, chunk_size=200, overlap=50)

    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    assert first_words[-50:] == second_words[:50]


def test_chunk_document_chunk_index_increments_across_sections():
    chunks = chunk_document("doc.md", MULTI_HEADING_DOC)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
