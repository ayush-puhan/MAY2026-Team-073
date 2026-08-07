"""ClubConnect AI Assistant - AI Content Generation (Phase 6B).

Per the Phase 6B spec Section 4: generate short, professional draft
text only. No SQL context, no persistence, no email sending - the
caller supplies whatever context the draft needs (event name, club
name, reason, etc.) in free text, and this module returns draft text
for them to review/edit/send themselves. Available to every
authenticated role (Section 5: every role gets "Content").
"""
from app.modules.ai_services.gemini_client import generate_response

# content_type -> (label, drafting instruction). Kept short and
# explicit per the spec's "Simple. Professional. Short." + "do NOT
# generate marketing content" rules.
CONTENT_TYPES = {
    "announcement": (
        "Announcement Draft",
        "Write a short, clear club/event announcement for platform members. "
        "Plain, informative tone - not a marketing pitch.",
    ),
    "event_description": (
        "Event Description",
        "Write a short, informative description of an event for a listing "
        "page - what it is, and why someone would want to attend.",
    ),
    "club_description": (
        "Club Description",
        "Write a short, welcoming description of a club for its profile "
        "page - what the club does and who it's for.",
    ),
    "invitation": (
        "Invitation Message",
        "Write a short, friendly invitation to an event or club.",
    ),
    "volunteer_recruitment": (
        "Volunteer Recruitment Message",
        "Write a short message recruiting volunteers for an event or task.",
    ),
    "reminder": (
        "Reminder Message",
        "Write a short, polite reminder about an upcoming deadline, event, "
        "or pending action.",
    ),
    "approval_comment": (
        "Approval Comment",
        "Write a short, professional comment approving a request (e.g. a "
        "budget, expense, event, or club proposal).",
    ),
    "rejection_message": (
        "Rejection Message",
        "Write a short, respectful message explaining that a request was "
        "not approved. Be constructive, not harsh, and do not fabricate a "
        "reason beyond what's given.",
    ),
    "budget_justification": (
        "Budget Justification",
        "Write a short, professional justification for a budget or expense "
        "request, suitable for a treasurer/faculty advisor to review.",
    ),
    "certificate_description": (
        "Certificate Description",
        "Write a short, formal description of achievement/participation "
        "suitable for a certificate.",
    ),
}


_CONTENT_PROMPT_PREFIX = (
    "You are drafting short, professional platform content for a university "
    "club management system. Follow the instruction below exactly. Use "
    "ONLY the details given - never invent a name, date, amount, or fact "
    "not present in them. Keep it short (a few sentences to a short "
    "paragraph). No markdown headers, no emojis, no marketing language. "
    "Return only the draft text, nothing else."
)


def generate_content(content_type: str, details: str, user) -> dict:
    """Generate one content draft.

    Returns {"content_type", "label", "authorized", "draft"}.
    ``authorized`` is False only when ``content_type`` isn't recognized
    (a client input error, not an access-control decision - every
    authenticated role may use every content type, per spec Section 5).
    """
    entry = CONTENT_TYPES.get(content_type)
    if entry is None:
        return {"content_type": content_type, "label": None, "authorized": False, "draft": None}

    label, instruction = entry
    details_text = (details or "").strip() or "(no additional details given)"

    prompt = (
        f"{_CONTENT_PROMPT_PREFIX}\n\n"
        f"Content type: {label}\n"
        f"Instruction: {instruction}\n"
        f"Requested by: {user.full_name}\n\n"
        f"Details supplied by the requester:\n{details_text}"
    )
    draft = generate_response(prompt)

    return {"content_type": content_type, "label": label, "authorized": True, "draft": draft}
