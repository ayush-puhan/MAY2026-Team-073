"""Unit tests for app/modules/ai_services/rag/loader.py (Phase 4).

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q
"""
from app.modules.ai_services.rag.loader import load_document, load_documents


def test_load_documents_reads_md_and_txt(tmp_path):
    (tmp_path / "a.md").write_text("# Title\n\nBody text.")
    (tmp_path / "b.txt").write_text("Plain text body.")
    (tmp_path / "c.ignored").write_text("should not be loaded")

    docs = load_documents(str(tmp_path))
    doc_ids = sorted(d.doc_id for d in docs)

    assert doc_ids == ["a.md", "b.txt"]


def test_load_documents_skips_empty_files(tmp_path):
    (tmp_path / "empty.md").write_text("   \n\n  ")
    (tmp_path / "real.md").write_text("content")

    docs = load_documents(str(tmp_path))

    assert [d.doc_id for d in docs] == ["real.md"]


def test_load_documents_missing_directory_returns_empty_list():
    assert load_documents("/no/such/directory/at/all") == []


def test_load_documents_is_sorted_and_non_recursive(tmp_path):
    (tmp_path / "z.md").write_text("z")
    (tmp_path / "a.md").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.md").write_text("nested")

    docs = load_documents(str(tmp_path))

    assert [d.doc_id for d in docs] == ["a.md", "z.md"]


def test_load_document_single_file(tmp_path):
    path = tmp_path / "only.md"
    path.write_text("hello")

    doc = load_document(str(path))

    assert doc.doc_id == "only.md"
    assert doc.text == "hello"


def test_load_document_missing_file_returns_none():
    assert load_document("/no/such/file.md") is None
