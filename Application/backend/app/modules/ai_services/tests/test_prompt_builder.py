"""Unit tests for app/modules/ai_services/prompt_builder.py (Phase 5A).

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q

Uses a small on-disk fixture "system" directory (via tmp_path) rather
than the real knowledge_base/system corpus, so these tests don't
depend on - or need updating alongside - the actual System Documents'
wording. An explicit `kb_system_dir` bypasses the process-wide cache
(see prompt_builder.load_system_documents), so each test is
independent.
"""
import pytest

from app.modules.ai_services import prompt_builder
from app.modules.ai_services.prompt_builder import (
    build_prompt,
    load_system_documents,
    reset_system_documents_cache,
)


@pytest.fixture()
def system_dir(tmp_path):
    d = tmp_path / "system"
    d.mkdir()
    (d / "a_first.md").write_text("# Doc A\nAlways-injected instructions A.")
    (d / "b_second.md").write_text("# Doc B\nAlways-injected instructions B.")
    return str(d)


@pytest.fixture(autouse=True)
def _clear_cache():
    reset_system_documents_cache()
    yield
    reset_system_documents_cache()


# ---------------------------------------------------------------------------
# load_system_documents
# ---------------------------------------------------------------------------


def test_load_system_documents_concatenates_all_docs(system_dir):
    combined = load_system_documents(system_dir)
    assert "Always-injected instructions A." in combined
    assert "Always-injected instructions B." in combined


def test_load_system_documents_missing_dir_returns_empty_string(tmp_path):
    missing = str(tmp_path / "does_not_exist")
    assert load_system_documents(missing) == ""


def test_load_system_documents_explicit_dir_bypasses_cache(system_dir, tmp_path):
    other_dir = tmp_path / "other_system"
    other_dir.mkdir()
    (other_dir / "only.md").write_text("Only doc.")

    first = load_system_documents(system_dir)
    second = load_system_documents(str(other_dir))

    assert first != second
    assert "Only doc." in second
    assert "Only doc." not in first


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


def _user_context():
    return {"user_id": 1, "full_name": "Asha Rao", "role": "student"}


def test_build_prompt_includes_system_docs(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Rewards", "How many points do I have?")
    assert "Always-injected instructions A." in prompt
    assert "Always-injected instructions B." in prompt


def test_build_prompt_includes_user_and_intent(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Rewards", "How many points do I have?")
    assert "Asha Rao" in prompt
    assert "role: student" in prompt
    assert "Detected intent: Rewards" in prompt
    assert "User message: How many points do I have?" in prompt


def test_build_prompt_formats_sql_context_as_json(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    sql_context = {"points_balance": 42, "recent_ledger": []}
    prompt = build_prompt(_user_context(), "Rewards", "points?", sql_context=sql_context)
    assert '"points_balance": 42' in prompt


def test_build_prompt_empty_sql_context_says_none(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Membership Process", "how do I join?", sql_context=None)
    assert "(none for this intent)" in prompt


def test_build_prompt_formats_rag_context_chunks(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    rag_context = [
        {"doc_id": "rewards_system_guide.md", "section_title": "Redeeming Points", "text": "Redeem via the Rewards tab."},
    ]
    prompt = build_prompt(_user_context(), "Rewards", "how do I redeem?", rag_context=rag_context)
    assert "[rewards_system_guide.md - Redeeming Points]" in prompt
    assert "Redeem via the Rewards tab." in prompt


def test_build_prompt_empty_rag_context_says_none_retrieved(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Rewards", "how many points?", rag_context=[])
    assert "(none retrieved for this turn)" in prompt


def test_build_prompt_no_history_says_no_prior_turns(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Rewards", "points?")
    assert "(no prior turns)" in prompt


def test_build_prompt_includes_history_when_given(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! How can I help?"},
    ]
    prompt = build_prompt(_user_context(), "Getting Started", "what is this app?", history=history)
    assert "user: Hi" in prompt
    assert "assistant: Hello! How can I help?" in prompt


def test_build_prompt_never_includes_unauthorized_marker_data(monkeypatch, system_dir):
    """Sanity check: build_prompt only ever renders what it's handed - it
    doesn't reach into the DB or RAG index itself, so passing no
    sql_context/rag_context must never fabricate any data-shaped
    content in the prompt."""
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Financial Operations", "our budget?", sql_context=None, rag_context=[])
    assert "(none for this intent)" in prompt
    assert "(none retrieved for this turn)" in prompt


# ---------------------------------------------------------------------------
# SQL-context priority instruction (Phase 6 final polish)
#
# Fixes the "several navigation/status questions return generic
# documentation instead of personalized SQL answers" issue: when SQL
# context exists for this turn, the prompt must explicitly tell Gemini
# to lead with it rather than defaulting to a generic dashboard-pointer
# answer.
# ---------------------------------------------------------------------------


def test_build_prompt_with_sql_context_includes_priority_instruction(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(
        _user_context(), "Membership", "which clubs am I a member of?",
        sql_context={"memberships": [{"club_name": "Robotics Club", "role_in_club": "member"}]},
    )
    assert "PRIORITY RULE" in prompt
    assert "authoritative" in prompt
    assert "Do NOT fall back to a generic dashboard pointer" in prompt


def test_build_prompt_without_sql_context_notes_none_fetched(monkeypatch, system_dir):
    monkeypatch.setattr(prompt_builder, "_resolve_kb_system_dir", lambda: system_dir)
    prompt = build_prompt(_user_context(), "Getting Started", "what is this app?", sql_context=None)
    assert "No SQL context was fetched for this turn" in prompt
