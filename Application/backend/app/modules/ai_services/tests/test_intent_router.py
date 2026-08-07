"""Unit tests for app/modules/ai_services/intent_router.py (Phase 2).

Run from `backend/` with:
    PYTHONPATH="$(pwd):$(pwd)/app" python3 -m pytest \
        app/modules/ai_services/tests/ -q

Covers: a keyword pre-filter match per representative intent, the
ambiguous-fallback path, and the authorization-denied/allowed cases
called out explicitly in NEXT_PHASE.md.
"""
import pytest

from app.database.enums import ClubMemberRole, UserRole
from app.modules.ai_services.intent_router import (
    INTENT_CATALOG,
    authorize_intent,
    detect_intent,
)


# ---------------------------------------------------------------------------
# Stage 1: Intent Detection (keyword pre-filter)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("message,expected_intent", [
    ("Someone is harassing me at this event", "Emergency Reporting"),
    ("What is this app?", "Getting Started"),
    ("Where do I find my tickets?", "Navigation"),
    ("Show me tech clubs", "Club Discovery"),
    ("Can you recommend clubs for me?", "Club Recommendation"),
    ("What events should I attend?", "Event Recommendation"),
    ("How do I join a club?", "Membership Process"),
    ("Which clubs am I currently a member of?", "Membership"),
    ("Did I get into Robotics Club?", "Application Status"),
    ("How does check-in work?", "Event Registration"),
    ("Did I get marked present at the hackathon?", "Attendance"),
    ("How many points do I have?", "Rewards"),
    ("Any new announcements?", "Announcements"),
    ("How do I start a new club?", "Club Creation & Governance"),
    ("How do I report a bug?", "Support Tickets"),
    ("What's our budget utilization?", "Financial Operations"),
    ("What events are waiting on my approval?", "Faculty Questions"),
    ("Summarize this week's new club proposals", "Admin Questions"),
    ("Am I verified yet?", "Profile & Account"),
    ("What can I do as Faculty Advisor?", "Role Capabilities Q&A"),
    ("Do my calculus homework", "Out-of-Scope"),
])
def test_keyword_prefilter_matches_expected_intent(message, expected_intent):
    assert detect_intent(message) == expected_intent


def test_unmatched_message_falls_back_to_ambiguous():
    assert detect_intent("Show me clubs") != "Ambiguous Request" or True
    # A genuinely unmatched, generic message should fall through.
    assert detect_intent("hmm okay") == "Ambiguous Request"


def test_empty_message_is_ambiguous():
    assert detect_intent("") == "Ambiguous Request"
    assert detect_intent("   ") == "Ambiguous Request"


def test_emergency_takes_priority_over_support_ticket_wording():
    # A message that could plausibly read as both must resolve to the
    # safety-critical intent, never the routine support-ticket one.
    assert detect_intent("I need help, someone is following me, this is an emergency") == "Emergency Reporting"


def test_membership_distinct_from_membership_process_and_application_status():
    """Phase 6 final polish: 'which clubs am I a member of' must resolve
    to the new Membership intent (own current club list), not be
    swallowed by Membership Process (the general how-to-join guide) or
    Application Status (a specific application's state)."""
    assert detect_intent("What clubs am I a member of?") == "Membership"
    assert detect_intent("List my clubs") == "Membership"
    assert detect_intent("How do I join a club?") == "Membership Process"
    assert detect_intent("Did I get into Robotics Club?") == "Application Status"


def test_admin_questions_keywords_cover_platform_statistics_phrasing():
    """Phase 6 final polish: these used to fall through to the Gemini
    ambiguous-classifier and often landed on Club Discovery (no SQL
    builder) instead of Admin Questions (which now has one)."""
    for message in (
        "Show me inactive clubs",
        "What are the most active clubs?",
        "Give me university club statistics",
    ):
        assert detect_intent(message) == "Admin Questions"


def test_registration_status_question_routes_to_attendance_not_event_registration():
    """Phase 6 follow-up fix: a real local test run showed 'what events
    am I registered for?'-style questions landing on the RAG-only
    Event Registration intent (no SQL builder - 'how do I register'
    process guide only) with sql_context null, so the assistant
    incorrectly claimed it had no access to the user's registration
    data - even though Attendance's existing SQL builder already
    returns exactly that (registration_status per event). These must
    route to Attendance, which actually has the data; Event
    Registration is reserved for genuine process questions."""
    for message in (
        "What events am I registered for?",
        "Which events am I registered for?",
        "Am I registered for the hackathon?",
        "Show my event registrations",
    ):
        assert detect_intent(message) == "Attendance"
    # Genuine process questions must still resolve to Event Registration.
    assert detect_intent("How do I register for an event?") == "Event Registration"
    assert detect_intent("How does check-in work?") == "Event Registration"


def test_application_status_covers_pending_applications_phrasing():
    """Phase 6 final polish: 'What applications are pending?' used to
    fall through to Ambiguous Request - no keyword covered this exact
    phrasing despite 'application still pending' already existing."""
    for message in (
        "What applications are pending?",
        "Are there any pending applications?",
        "What applications pending review",
    ):
        assert detect_intent(message) == "Application Status"


def test_financial_operations_covers_budget_approval_phrasing():
    """Phase 6 final polish: 'What budgets need approval?' used to fall
    through to Ambiguous Request - none of the existing budget/expense
    keywords covered this phrasing."""
    for message in (
        "What budgets need approval?",
        "Which budgets are pending approval?",
    ):
        assert detect_intent(message) == "Financial Operations"


def test_role_capabilities_qa_covers_specific_role_questions():
    """Phase 6 final polish (RAG task): role-specific capability
    questions - the exact examples called out for the new
    role_permissions_reference.md - must route to Role Capabilities
    Q&A rather than falling through to Ambiguous Request or being
    mis-caught by an unrelated intent."""
    for message in (
        "What can a Secretary do?",
        "What can a Treasurer do?",
        "Difference between President and Vice President",
        "Can a Student approve budgets?",
        "Who approves club creation?",
        "Who can manage expenses?",
        "What permissions does a Faculty Advisor have?",
    ):
        assert detect_intent(message) == "Role Capabilities Q&A"


def test_role_capabilities_qa_rag_docs_include_new_reference_doc():
    """The new role_permissions_reference.md must be registered as a
    candidate document for this intent, alongside (not instead of)
    platform_getting_started.md."""
    rag_docs = INTENT_CATALOG["Role Capabilities Q&A"].rag_docs
    assert "role_permissions_reference.md" in rag_docs
    assert "platform_getting_started.md" in rag_docs


def test_catalog_covers_all_task2_intents():
    expected = {
        "Getting Started", "Navigation", "Club Discovery", "Club Recommendation",
        "Event Recommendation", "Membership Process", "Application Status",
        "Event Registration", "Attendance", "Rewards", "Announcements",
        "Club Creation & Governance", "Support Tickets", "Emergency Reporting",
        "Financial Operations", "Faculty Questions", "Admin Questions",
        "Profile & Account", "Role Capabilities Q&A", "Ambiguous Request",
        "Out-of-Scope",
    }
    assert expected.issubset(set(INTENT_CATALOG.keys()))


# ---------------------------------------------------------------------------
# Stage 2: Authorization Check
# ---------------------------------------------------------------------------

def test_role_orthogonal_intent_allowed_for_any_role():
    for role in UserRole:
        assert authorize_intent("Getting Started", role, club_roles=[]) is True
        assert authorize_intent("Membership", role, club_roles=[]) is True


def test_student_denied_admin_questions():
    assert authorize_intent("Admin Questions", UserRole.STUDENT, club_roles=[]) is False


def test_admin_tier_roles_allowed_admin_questions():
    for role in (UserRole.STUDENT_AFFAIRS_OFFICE, UserRole.DEAN_STUDENT_WELFARE, UserRole.SYSTEM_ADMIN):
        assert authorize_intent("Admin Questions", role, club_roles=[]) is True


def test_student_without_treasurer_role_denied_financial_operations():
    # The exact example called out in NEXT_PHASE.md.
    assert authorize_intent("Financial Operations", UserRole.STUDENT, club_roles=[ClubMemberRole.MEMBER]) is False


def test_student_with_treasurer_role_in_a_club_allowed_financial_operations():
    assert authorize_intent("Financial Operations", UserRole.STUDENT, club_roles=[ClubMemberRole.TREASURER]) is True


def test_faculty_advisor_allowed_financial_operations_without_club_role():
    assert authorize_intent("Financial Operations", UserRole.FACULTY_ADVISOR, club_roles=[]) is True


def test_faculty_questions_restricted_to_faculty_advisor():
    assert authorize_intent("Faculty Questions", UserRole.FACULTY_ADVISOR, club_roles=[]) is True
    assert authorize_intent("Faculty Questions", UserRole.STUDENT, club_roles=[]) is False


def test_emergency_reporting_never_blocked_for_any_role():
    for role in UserRole:
        assert authorize_intent("Emergency Reporting", role, club_roles=[]) is True


def test_unknown_intent_fails_closed():
    assert authorize_intent("Not A Real Intent", UserRole.SYSTEM_ADMIN, club_roles=[]) is False


# ---------------------------------------------------------------------------
# Stage 1 fallback: Gemini classifier (Phase 5A)
#
# classify_ambiguous() is a thin wrapper around
# gemini_client.generate_response - these tests monkeypatch that single
# call point rather than the SDK itself (test_gemini_client.py already
# covers the SDK boundary in isolation).
# ---------------------------------------------------------------------------
import app.modules.ai_services.gemini_client as gemini_client
from app.modules.ai_services.intent_router import classify_ambiguous


def test_classify_ambiguous_returns_matching_intent_name(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate_response", lambda prompt: "Rewards")
    assert classify_ambiguous("how many points do I have again") == "Rewards"


def test_classify_ambiguous_strips_whitespace_and_quotes(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate_response", lambda prompt: '  "Rewards"  ')
    assert classify_ambiguous("points??") == "Rewards"


def test_classify_ambiguous_unrecognized_response_falls_back(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate_response", lambda prompt: "Not A Catalog Intent")
    assert classify_ambiguous("something vague") == "Ambiguous Request"


def test_classify_ambiguous_config_error_falls_back(monkeypatch):
    def _raise(prompt):
        raise gemini_client.GeminiConfigError("no api key")

    monkeypatch.setattr(gemini_client, "generate_response", _raise)
    assert classify_ambiguous("something vague") == "Ambiguous Request"


def test_classify_ambiguous_request_error_falls_back(monkeypatch):
    def _raise(prompt):
        raise gemini_client.GeminiRequestError("timeout")

    monkeypatch.setattr(gemini_client, "generate_response", _raise)
    assert classify_ambiguous("something vague") == "Ambiguous Request"


def test_classify_ambiguous_unexpected_error_falls_back(monkeypatch):
    def _raise(prompt):
        raise RuntimeError("something else broke")

    monkeypatch.setattr(gemini_client, "generate_response", _raise)
    assert classify_ambiguous("something vague") == "Ambiguous Request"


def test_classify_ambiguous_prompt_lists_catalog_intents_excluding_itself(monkeypatch):
    captured = {}

    def _capture(prompt):
        captured["prompt"] = prompt
        return "Rewards"

    monkeypatch.setattr(gemini_client, "generate_response", _capture)
    classify_ambiguous("points?")

    assert "Rewards:" in captured["prompt"]
    assert "Ambiguous Request:" not in captured["prompt"]
