"""Knowledge Base Loader.

Reads plain-text knowledge base documents from disk. Markdown and
``.txt`` are supported unconditionally; PDF support is optional and only
used if ``pypdf`` happens to be installed - it is not a hard dependency
of this phase, since the current knowledge base is Markdown only (see
NEXT_PHASE.md).
"""
import os
from dataclasses import dataclass

SUPPORTED_TEXT_EXTENSIONS = (".md", ".markdown", ".txt")
_PDF_EXTENSION = ".pdf"


@dataclass(frozen=True)
class LoadedDocument:
    doc_id: str        # filename, e.g. "financial_operations_guide.md"
    path: str           # absolute path on disk
    text: str           # raw file content


def _read_pdf(path: str) -> str:
    """Best-effort PDF text extraction. Returns "" if pypdf isn't available."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""

    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_documents(directory: str, extensions=None) -> "list[LoadedDocument]":
    """Load every supported document in ``directory`` (non-recursive).

    Returns an empty list if ``directory`` doesn't exist, rather than
    raising - the caller (retrieval_service) decides whether an empty
    corpus is an error.
    """
    if not os.path.isdir(directory):
        return []

    allowed = tuple(extensions) if extensions else SUPPORTED_TEXT_EXTENSIONS
    documents = []
    for filename in sorted(os.listdir(directory)):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext in allowed:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == _PDF_EXTENSION:
            text = _read_pdf(path)
        else:
            continue

        if text.strip():
            documents.append(LoadedDocument(doc_id=filename, path=path, text=text))

    return documents


def load_document(path: str) -> "LoadedDocument | None":
    """Load a single document by path, or None if missing/unreadable."""
    if not os.path.isfile(path):
        return None

    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()
    if ext == _PDF_EXTENSION:
        text = _read_pdf(path)
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    if not text.strip():
        return None
    return LoadedDocument(doc_id=filename, path=path, text=text)
