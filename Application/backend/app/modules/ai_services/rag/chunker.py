"""Chunking.

Heading-aware Markdown chunking (splits on ``#``/``##``/... headings so
each chunk stays within one logical section), falling back to a plain
sliding window for text with no headings or for any single section that
is still too large. Target size is expressed in words (a simple, fast
stand-in for tokens - good enough at this corpus's scale; NEXT_PHASE.md's
~300-500 token target maps to roughly the same range in words).
"""
import re
from dataclasses import dataclass

DEFAULT_CHUNK_SIZE = 350   # target words per chunk
DEFAULT_OVERLAP = 50        # words of overlap between sliding-window chunks

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    section_title: str
    text: str
    chunk_index: int


def _split_by_heading(text: str):
    """Split Markdown text into (section_title, section_body) pairs.

    The first pair's title is "" if the document has content before its
    first heading (e.g. a lead-in paragraph). Returns [("", text)] if the
    document has no headings at all.
    """
    matches = list(_HEADING_RE.finditer(text))
    if not matches:
        return [("", text)]

    sections = []
    if matches[0].start() > 0:
        preamble = text[:matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append((title, body))

    return sections


def _sliding_window(words: "list[str]", chunk_size: int, overlap: int):
    """Yield overlapping word-windows. overlap must be < chunk_size."""
    if not words:
        return
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        window = words[start:start + chunk_size]
        if not window:
            break
        yield " ".join(window)
        if start + chunk_size >= len(words):
            break


def chunk_document(
    doc_id: str,
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> "list[Chunk]":
    """Chunk one document's text into heading-scoped, size-bounded pieces.

    Each Markdown section becomes its own chunk when it fits within
    ``chunk_size`` words; oversized sections (or documents with no
    headings) fall back to a sliding window within that section so no
    single chunk balloons past the target size.
    """
    chunks = []
    index = 0
    for title, body in _split_by_heading(text):
        if not body:
            continue
        words = body.split()
        if len(words) <= chunk_size:
            chunks.append(Chunk(doc_id=doc_id, section_title=title, text=body, chunk_index=index))
            index += 1
        else:
            for window_text in _sliding_window(words, chunk_size, overlap):
                chunks.append(Chunk(doc_id=doc_id, section_title=title, text=window_text, chunk_index=index))
                index += 1

    return chunks


def chunk_documents(documents, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
    """Chunk a list of loader.LoadedDocument (or doc_id/text-alike) objects."""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc.doc_id, doc.text, chunk_size, overlap))
    return all_chunks
