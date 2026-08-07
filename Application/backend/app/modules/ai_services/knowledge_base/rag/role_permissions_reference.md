# Role & Permissions Reference

## Purpose

A single authoritative reference for what each ClubConnect role is and what it can and cannot do. This document exists because `platform_getting_started.md` covers roles only at a summary level (one paragraph for "Club Officer" as a whole), which is not enough detail to answer role-specific questions like "what can a Secretary do?" or "what's the difference between a President and a Vice President?" accurately. This document gives each role its own entry and states plainly, per role, what is backed by real backend behavior versus what is Software Design Document (SDD) intent not yet implemented as a working feature. Nothing in this document should be treated as inventing a permission — where the SDD describes something this backend does not yet enforce or expose, that gap is called out explicitly rather than glossed over.

## Document Scope and Sources

This document is built strictly from two sources:
1. **The Software Design Document** (Section 4.2 "User Roles", 4.3 "Role Hierarchy", 4.4 "Permission Matrix", 4.5 "Dashboard Allocation").
2. **This backend's actual implementation**: `app/database/enums.py` (`UserRole`, `ClubMemberRole`, `CommitteeRole`), `app/database/models/` (schema), `app/modules/ai_services/intent_router.py` (the only place role-based authorization is currently enforced), and `app/modules/ai_services/sql_context_builder.py` (what data each role can actually retrieve through the assistant).

Where the two sources disagree or where the SDD describes a role/action this backend does not yet implement, this document says so directly rather than presenting SDD intent as working behavior.

## Two Role Layers (recap)

As established in `platform_getting_started.md`: **platform role** (`users.role`) is the account's tier across the whole platform; **club-scoped role** (`club_memberships.role_in_club`) applies only within one specific club. A person's platform role never changes because of a club role they hold. This document treats those as two separate lists — "Platform Roles" and "Club Roles" — and does not mix them.

A person browsing without an account (a "Guest User" in the SDD's role hierarchy diagram) is not a `UserRole` value in this backend — there is no authenticated "guest" role. Unauthenticated browsing of public clubs/events is a product-level concept, not an account role, and is out of scope for this reference.

---

# Platform Roles

## Student

**Purpose:** The default account tier for every person who signs up on ClubConnect; the base platform role from which all club-level participation (as a member or officer) happens.

**Responsibilities:** Discovering and joining clubs, registering for and attending events, tracking their own reward points, maintaining their profile, and raising support tickets or emergency reports.

**Allowed Actions:** Browse/search clubs and events; apply to join clubs; register for events; view their own membership, application, attendance, and reward-point data; ask the assistant for personalized club/event recommendations; submit club-creation proposals; raise support tickets; file emergency reports; hold any `role_in_club` (member or officer-level) in one or more clubs while remaining platform role "student."

**Restricted Actions:** Cannot approve club-join applications, approve or manage another club's budget/expenses, access `Financial Operations` or `Faculty Questions` or `Admin Questions` intents (all three are role-gated and denied to a plain student per `intent_router.py`), or view any other individual student's application, ticket, or financial data.

**Typical AI Questions:** "What clubs am I in?", "Did I get into Robotics Club?", "How many reward points do I have?", "What events am I registered for?", "How do I start a new club?"

**Related Modules:** Student module (`app/modules/student` — implemented and registered), Users module (profile), AI Assistant (all role-orthogonal intents).

**Permission Notes:** A student who also holds an officer-level `role_in_club` (e.g. treasurer, president) gains additional capabilities, but only within that specific club — see the Club Roles section below. This does not change their platform role.

---

## Faculty Advisor

**Purpose:** Provides institutional oversight for the specific clubs assigned to them (`clubs.faculty_advisor_id`).

**Responsibilities:** Per the SDD: monitor club operations, approve activities, oversee compliance and finances for advised clubs.

**Allowed Actions (backend-confirmed):** Reach the `Faculty Questions` and `Financial Operations` intents (both explicitly allow `UserRole.FACULTY_ADVISOR` in `intent_router.py`), and through them retrieve — for clubs where they are the assigned `faculty_advisor_id` — the club roster/status list, events with `status = pending_approval`, and a budget/expense snapshot (allocated totals, expense approval breakdown, recent expenses). A faculty advisor reaching `Financial Operations` sees figures for every club they advise, not only clubs where they separately hold a treasurer membership (they don't — `role_in_club` is student-side only).

**Restricted Actions:** Cannot reach `Admin Questions` (platform-wide oversight is restricted to Student Affairs Office / Dean of Student Welfare / System Admin only). Has no visibility into clubs they do not advise. This backend has **no implemented endpoint to actually approve an event or expense** — the `faculty` module's route file (`app/modules/faculty/routes.py`) is an empty stub and is not registered in `app/api.py`. The AI assistant can currently only report *what* is pending, not perform the approval itself.

**Typical AI Questions:** "What clubs do I advise?", "What events are waiting on my approval?", "What's our budget utilization?", "What am I allowed to do as Faculty Advisor?"

**Related Modules:** Faculty module (`app/modules/faculty` — route file present but empty, not wired into `api.py`), AI Assistant `Faculty Questions` / `Financial Operations` intents (implemented, read-only).

**Permission Notes:** Faculty Dashboard → "Pending Approvals" and "Club Analytics" are named as dashboard locations in `dashboard_redundancy_map.md` §4, but no faculty-facing API route exists yet in this backend to serve or act on them outside the AI assistant's own SQL context builders.

---

## Student Affairs Office

**Purpose:** One of three platform-wide administrative roles (alongside Dean of Student Welfare and System Admin) responsible for university-level club governance.

**Responsibilities:** Per the SDD: review club proposals, monitor governance, oversee university-wide club operations.

**Allowed Actions (backend-confirmed):** Reach the `Admin Questions` intent (`intent_router.py` explicitly allows this role), which returns club status breakdown, inactive-club listing, most-active clubs, and club-creation-request throughput and history — scoped to the caller's own university tenant where `university_id` is set.

**Restricted Actions:** Cannot see another individual student's application, ticket, or financial record as a raw row — `Admin Questions` returns aggregates and proposal-level data only, never individual data outside the caller themself, per `assistant_conversation_behavior.md` §2 and §10.

**Typical AI Questions:** "Summarize this week's new club proposals", "Show me inactive clubs", "What are the most active clubs?"

**Related Modules:** University Administration module (`app/modules/university_administration/routes.py` — empty stub, not registered in `api.py`), AI Assistant `Admin Questions` intent (implemented, read-only).

**Permission Notes:** The SDD's "Club Creation Approval" permission (making the actual approve/reject decision on a `club_creation_requests` row) has no implemented write endpoint in this backend. The AI assistant can report request status and counts; it cannot record a decision.

---

## Dean of Student Welfare

**Purpose:** The most senior platform-wide administrative role in the SDD's role hierarchy, above Student Affairs Office.

**Responsibilities:** Per the SDD: institutional oversight, policy enforcement, strategic governance.

**Allowed Actions (backend-confirmed):** Identical `Admin Questions` access to Student Affairs Office — `intent_router.py` grants both roles (and System Admin) the same `allowed_platform_roles` set for this intent. This backend does **not** implement any additional capability, escalation path, or data visibility that distinguishes Dean of Student Welfare from Student Affairs Office; the two are functionally identical in the current implementation despite sitting at different tiers in the SDD's hierarchy diagram.

**Restricted Actions:** Same as Student Affairs Office — no individual-level data outside authorized aggregate/proposal review.

**Typical AI Questions:** Same as Student Affairs Office — "Give me university club statistics", "What are the engagement trends?"

**Related Modules:** Same as Student Affairs Office; no dedicated module or route exists for this role specifically.

**Permission Notes:** If a future phase needs to differentiate this role from Student Affairs Office (e.g. a policy-level action only the Dean can take), that distinction does not exist anywhere in the current backend and would need to be added — this document does not assume or invent one.

---

## System Administrator

**Purpose:** The platform's technical/operational administrator role.

**Responsibilities:** Per the SDD: system administration, alongside the same platform-wide oversight granted to the other two admin-tier roles.

**Allowed Actions (backend-confirmed):** Same `Admin Questions` access as Student Affairs Office and Dean of Student Welfare (`intent_router.py` grants all three the same intent access). The SDD's Permission Matrix additionally marks System Administration itself as a module only this role can access, but that module has no backend implementation in this codebase (no user-management, role-assignment, or system-configuration endpoints exist).

**Restricted Actions:** Same aggregate-only data boundary as the other two admin-tier roles.

**Typical AI Questions:** Same as the other admin-tier roles through the AI assistant; system-administration questions (e.g. "how do I change a user's role") are outside the assistant's scope entirely, since no such feature is implemented.

**Related Modules:** No dedicated "System Administration" module exists in `app/modules/`. AI Assistant `Admin Questions` intent is the only implemented capability tied to this role.

**Permission Notes:** In this backend, System Admin is functionally indistinguishable from the other two admin-tier roles for every capability that actually exists — the SDD's "System Administration" row in the Permission Matrix currently corresponds to no working feature.

---

# Club Roles (`club_memberships.role_in_club`)

Club roles apply only within the specific club where the membership record's `status = approved`. A person can hold different (or no) club roles across different clubs simultaneously, and holding an officer-level club role never changes their platform role. The default role assigned on membership approval is **Member** (`membership_process_guide.md`).

The backend's `ClubMemberRole` enum contains exactly these values: `applicant`, `member`, `volunteer_coordinator`, `event_coordinator`, `secretary`, `treasurer`, `vice_president`, `president`. (`applicant` is a transitional pre-approval state, not a role covered in this reference.)

**Important backend-implementation note that applies to every club role below:** the AI assistant's authorization layer (`intent_router.py`) currently distinguishes club roles in exactly **one** place — the `Financial Operations` intent, which requires `role_in_club == treasurer` specifically. No other intent, and no other part of this backend, currently checks *which* officer-level role a person holds. This means that, as far as the working backend is concerned, President, Vice President, Secretary, Event Coordinator, and Volunteer Coordinator are all currently treated identically by the AI assistant and by authorization — none of them unlocks any assistant capability beyond what a plain Member already has, except by virtue of being an approved club member at all. The differentiated responsibilities below are the SDD's intended design; they are **not yet gated or enforced anywhere in this backend**, because the modules that would implement them (`club_leadership`, `treasurer`) are empty route-file stubs not registered in `app/api.py`. This gap is stated once here and referenced from each role entry rather than repeated in full each time.

## Member

**Purpose:** The baseline, non-officer role every approved club participant holds unless assigned an officer-level role.

**Responsibilities:** Participate in club activities; access internal club resources; download certificates.

**Allowed Actions:** Everything a Student can do platform-wide, plus club-specific participation: viewing internal club resources/documents, downloading certificates, joining committees (per `membership_process_guide.md`, committee assignment requires an existing approved membership in the parent club).

**Restricted Actions:** Cannot approve applications, manage the club's events or budget, or act on behalf of the club administratively.

**Typical AI Questions:** "What clubs am I a member of?", "Am I on any committees?"

**Related Modules:** Club Leadership module (`app/modules/club_leadership/routes.py` — empty stub, not registered).

**Permission Notes:** None beyond the general note above — Member has no officer-level capabilities by definition.

---

## Committee Member

**Backend-mapping note (read first):** "Committee Member" is **not** a `ClubMemberRole` value. It is a separate dimension entirely: the `CommitteeRole` enum (`head`, `co_head`, `member`), assigned via the `committee_memberships` table, which links an existing `ClubMembership` to a `Committee` within that club. A person must already hold an approved club membership (any `role_in_club`) before they can be added to a committee — committee membership is layered on top of, not a substitute for, a club role. Referring to "Committee Member" as if it were a `role_in_club` value (as the SDD's role-hierarchy diagram implies) does not match this backend's schema.

**Purpose:** Represents participation in one of a club's optional sub-groups (e.g. "Events Committee," "Outreach Committee").

**Responsibilities:** Per the SDD: assist with club operations, manage volunteers, coordinate activities — understood here as committee-level participation, not a club-wide officer role.

**Allowed Actions:** Whatever the underlying `role_in_club` already grants (typically Member-level), plus association with a specific committee's scope of work. `CommitteeRole.head` / `co_head` may carry additional committee-internal coordination responsibility per the SDD, but this backend has no implemented endpoint that grants `CommitteeRole` any capability beyond the underlying club role.

**Restricted Actions:** Same restrictions as whatever `role_in_club` the person holds; committee assignment itself confers no additional platform or club-wide authorization in this backend.

**Typical AI Questions:** "What committee am I on?", "Who's on the Events Committee?" — note that no current AI intent or SQL builder retrieves committee membership; this data exists in the schema (`committees`, `committee_memberships`) but is not yet exposed through the assistant.

**Related Modules:** Club Leadership module (empty stub); `committees` / `committee_memberships` tables exist and are populated but have no dedicated intent or SQL context builder.

**Permission Notes:** Do not confuse this with a `role_in_club` value — see the mapping note above.

---

## Volunteer Coordinator

**Purpose:** A club officer role focused on volunteer management for club activities and events.

**Responsibilities:** Per the SDD: assign volunteer duties, monitor volunteer participation. Schema support exists for this via the `volunteer_assignments` relationship on `ClubMembership`.

**Allowed Actions (SDD-intended, not backend-enforced beyond Member-level):** Assign and track volunteer tasks tied to the club's events. See the general club-role note above — this backend does not currently gate any capability specifically to `role_in_club == volunteer_coordinator`.

**Restricted Actions:** Same platform-wide restrictions as any Member (cannot access Financial Operations, Faculty Questions, or Admin Questions on the strength of this role alone).

**Typical AI Questions:** "What are my responsibilities as Volunteer Coordinator?"

**Related Modules:** Club Leadership module (empty stub).

**Permission Notes:** The SDD's Permission Matrix places "Coordinator"-tier roles (which this document interprets as Volunteer Coordinator and Event Coordinator) at Event Management / Attendance Monitoring / Announcement Management access. No backend code currently checks for this specific role value to grant those.

---

## Event Coordinator

**Purpose:** A club officer role focused on organizing and running the club's events.

**Responsibilities:** Per the SDD: create and manage events, track attendance, monitor event safety.

**Allowed Actions (SDD-intended, not backend-enforced beyond Member-level):** Create/manage the club's events, track attendance. See the general club-role note above.

**Restricted Actions:** Same platform-wide restrictions as any Member.

**Typical AI Questions:** "What are my responsibilities as Event Coordinator?"

**Related Modules:** Club Leadership module (empty stub); Events schema (`app/database/models/events.py`) supports event/attendance data, but event-creation is not exposed through any registered API route in this backend.

**Permission Notes:** Retains all Member-level capabilities in addition to any event-management responsibility, consistent with `event_lifecycle_guide.md`'s general "officer-level roles carry additional capabilities scoped to that specific club" framing — but that framing is SDD intent, not an enforced backend check for this specific role value.

---

## Secretary

**Purpose:** A club officer role focused on documentation and communication.

**Responsibilities:** Per the SDD: manage club documentation, announcements, meeting records, and communication.

**Allowed Actions (SDD-intended, not backend-enforced beyond Member-level):** Post announcements, maintain documents/meeting-minutes records. See the general club-role note above.

**Restricted Actions:** Same platform-wide restrictions as any Member. Cannot approve budgets or expenses (that is Treasurer/Faculty territory per the SDD, and this backend's only role-specific gate — Financial Operations — requires `treasurer`, not `secretary`).

**Typical AI Questions:** "What can a Secretary do?", "What's the difference between a Secretary and a Treasurer?"

**Related Modules:** Club Leadership module (empty stub); `Announcement` model exists and is populated, with `posted_by` referencing any user, but no role check restricts who may post one in this backend.

**Permission Notes:** No backend code currently distinguishes Secretary from Member for any assistant capability.

---

## Treasurer

**Purpose:** The one club officer role this backend actually distinguishes from the rest — responsible for the club's financial operations.

**Responsibilities:** Per the SDD: budget planning, expense tracking, financial approvals, AI financial analytics.

**Allowed Actions (backend-confirmed):** Reach the `Financial Operations` intent — `intent_router.py` requires `requires_club_role=ClubMemberRole.TREASURER` for any non-faculty-advisor caller. Through it, retrieve budget/expense figures (allocated amounts, expense approval breakdown, recent expenses) **only for the specific club(s) where they hold an approved treasurer membership** — `sql_context_builder.py`'s `_treasurer_club_ids` re-derives this from the caller's own rows, so a treasurer of Club A never sees Club B's figures.

**Restricted Actions:** Cannot access `Faculty Questions` or `Admin Questions`. This backend has **no implemented endpoint to create a budget, submit an expense, or record an approval decision** — the `treasurer` module's route file is an empty stub, not registered in `api.py`. The assistant can report existing figures; it cannot perform financial actions.

**Typical AI Questions:** "What's our budget utilization?", "Our club's finances", "What budgets need approval?"

**Related Modules:** Treasurer module (`app/modules/treasurer/routes.py` — empty stub, not registered); AI Assistant `Financial Operations` intent (implemented, read-only); `Budget` / `Expense` models (schema fully implemented, embedded approval fields per `financial_operations_guide.md`).

**Permission Notes:** This is the only club-scoped role the AI assistant's authorization layer checks by name. Every other club officer role is currently role-orthogonal to the assistant.

---

## Vice President

**Purpose:** A club officer role supporting the President.

**Responsibilities:** Per the SDD: assist the President and supervise club operations.

**Allowed Actions (SDD-intended, not backend-enforced beyond Member-level):** General club operational supervision alongside the President. See the general club-role note above — no backend behavior currently differs for `vice_president` versus any other officer role, or versus `member`.

**Restricted Actions:** Same platform-wide restrictions as any Member. No backend-enforced distinction between what a Vice President and a President can do — see the President entry below for the same caveat from the other side.

**Typical AI Questions:** "What's the difference between President and Vice President?"

**Related Modules:** Club Leadership module (empty stub).

**Permission Notes:** The SDD's org-chart image places Vice President, Secretary, and Treasurer as siblings reporting into "Club Leadership" alongside President — but only Treasurer has any backend-enforced distinction (see above). If asked directly what separates Vice President from President in this backend, the honest answer is: nothing is currently enforced differently between them; the SDD describes Vice President as an assistant/supervisory role to the President, but no code checks for `vice_president` specifically anywhere in this codebase.

---

## President

**Purpose:** The senior-most club officer role.

**Responsibilities:** Per the SDD: manage overall club operations, approve memberships, oversee activities.

**Allowed Actions (SDD-intended, not backend-enforced beyond Member-level):** Approve/reject club-join applications, general club oversight. See the general club-role note above — this backend has no implemented membership-approval endpoint role-gated to `president`; the `club_memberships.approved_by` field can reference any user id, with no role check enforced at the model layer, and the module that would implement an approval endpoint (`club_leadership`) is an empty stub.

**Restricted Actions:** Same platform-wide restrictions as any Member — cannot reach Financial Operations, Faculty Questions, or Admin Questions on the strength of holding this role alone (Financial Operations specifically requires the `treasurer` role, not `president`).

**Typical AI Questions:** "What can a President do that a Member can't?", "Who approves club membership applications?"

**Related Modules:** Club Leadership module (empty stub, not registered in `api.py`).

**Permission Notes:** The SDD names President as the role that "approves memberships," but as with every non-Treasurer club role, this backend does not currently enforce that at the code level — any authenticated write to `club_memberships.status`/`approved_by` would need to be added in a future phase. State this plainly if asked who is *currently* able to approve a membership in this backend: no role-gated approval endpoint exists yet.

---

# Permission Matrix

The table below mirrors the Software Design Document's Section 4.4 Permission Matrix exactly (rows/columns and ✓/— marks unchanged). The SDD's column headers are broader tiers than the individual `ClubMemberRole` values documented above; this document interprets that mapping once, explicitly, immediately below the table, rather than inside each cell.

| Module | Student | Member | Coordinator | Leadership | Treasurer | Faculty | University Admin |
|---|---|---|---|---|---|---|---|
| Browse Clubs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Membership Application | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Membership Approval | — | — | — | ✓ | — | ✓ | ✓ |
| Event Registration | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Event Management | — | — | ✓ | ✓ | — | ✓ | ✓ |
| Attendance Monitoring | — | — | ✓ | ✓ | — | ✓ | ✓ |
| Announcement Management | — | — | ✓ | ✓ | — | ✓ | ✓ |
| Budget Management | — | — | — | — | ✓ | ✓ | ✓ |
| Expense Tracking | — | — | — | — | ✓ | ✓ | ✓ |
| Financial Reports | — | — | — | — | ✓ | ✓ | ✓ |
| AI Analytics | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Helpdesk | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Emergency Reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Club Creation Approval | — | — | — | — | — | ✓ | ✓ |
| System Administration | — | — | — | — | — | — | ✓ |

**Column-to-role mapping used above (SDD tiers → this backend's actual role values):**
- **Student** = platform role `student` with no club membership, or the platform-wide capabilities any student has regardless of club role.
- **Member** = `role_in_club = member`.
- **Coordinator** = this document's interpretation of `role_in_club = volunteer_coordinator` or `event_coordinator`. The SDD does not itself define "Coordinator" further than this heading.
- **Leadership** = this document's interpretation of `role_in_club = secretary`, `vice_president`, or `president` (officer-level roles other than treasurer).
- **Treasurer** = `role_in_club = treasurer`.
- **Faculty** = platform role `faculty_advisor`.
- **University Admin** = platform role `student_affairs_office`, `dean_student_welfare`, or `system_admin`.

**Backend-enforcement status, row by row:**
- **Browse Clubs, Membership Application, Event Registration, AI Analytics, Helpdesk, Emergency Reports** — implemented and role-orthogonal (every authenticated role can reach these), matching the all-✓ rows.
- **Financial Reports (as "own club's figures")** — implemented for Treasurer and Faculty via the `Financial Operations` intent, scoped to the caller's own club(s) as described above.
- **Membership Approval, Event Management, Attendance Monitoring, Announcement Management, Budget Management, Expense Tracking, Club Creation Approval, System Administration** — these are SDD-intended permissions with **no enforcing backend code** in this snapshot (the modules that would implement them — `club_leadership`, `treasurer`, `faculty`, `university_administration` — are empty route-file stubs not registered in `app/api.py`). Do not tell a user these actions are currently available through the platform; the schema and design support them, but the write-endpoints do not exist yet.

---

# Frequently Asked Questions

**What can a Secretary do that a Member can't?**
Per the SDD, a Secretary manages club documentation, announcements, and meeting records. In this backend, no code currently enforces that distinction — a Secretary has the same actually-available capabilities as a Member, since the module that would implement Secretary-specific actions is not built yet.

**What can a Treasurer do?**
A Treasurer can — through the AI assistant — retrieve their club's budget and expense figures (the `Financial Operations` intent). This is the one club-scoped role this backend's authorization layer actually checks by name. Creating budgets or recording approvals is SDD-intended but has no implemented endpoint yet.

**What's the difference between President and Vice President?**
Per the SDD, the President manages overall club operations and approves memberships; the Vice President assists the President and supervises club operations. In this backend, neither role currently has any enforced capability beyond what a Member has — the distinction is present in the design, not yet in the code.

**Can a Student approve budgets?**
No. Budget-related figures are only retrievable through `Financial Operations`, which requires holding the `treasurer` role in that specific club (or being `faculty_advisor` for an advised club). A plain student platform role with no such club role cannot reach this intent at all. No role in this backend can currently *approve* a budget through a working endpoint — that capability isn't implemented yet.

**Who approves club creation?**
Per the SDD and `club_creation_governance_guide.md`, a reviewer records an approve/reject decision on a `club_creation_requests` row; `Admin Questions` access (Student Affairs Office, Dean of Student Welfare, System Admin) is the intended reviewer tier. This backend has no implemented endpoint that performs that approval — only the AI assistant's read-only status/aggregate reporting exists today.

**Who can manage expenses?**
Per the SDD, Treasurer, Faculty, and University Admin. In this backend, only Treasurer and Faculty Advisor can currently *view* expense figures for their own club(s) through `Financial Operations`; no role can currently submit or approve an expense through a working endpoint.

**What permissions does a Faculty Advisor have?**
A Faculty Advisor can reach `Faculty Questions` (advised-club oversight: roster, pending event approvals, budget snapshot) and `Financial Operations` (budget/expense figures for advised clubs), both scoped to the clubs where they are the assigned `faculty_advisor_id`. They cannot reach `Admin Questions` (platform-wide, admin-tier only).

---

# Common Mistakes

- Assuming "Committee Member" is a `role_in_club` value — it is not; it's a separate `CommitteeRole` (head/co_head/member) layered on top of an existing club membership.
- Assuming any club officer role other than Treasurer unlocks an assistant capability — currently only `treasurer` is checked by name anywhere in the authorization layer.
- Assuming the SDD's Permission Matrix rows describing write actions (approvals, budget creation, event management) are live features — most have no backend-enforced or backend-implemented endpoint in this snapshot; only the read-side AI assistant intents for these areas are implemented.
- Assuming Dean of Student Welfare has broader access than Student Affairs Office — in this backend they are functionally identical.
- Treating a faculty advisor's access as platform-wide — it is scoped strictly to the clubs where they are the assigned advisor.

---

# Important Notes

- This document intentionally documents gaps between the SDD and the working backend rather than smoothing over them — this is a deliberate design choice for this reference, matching the project's hallucination-prevention principle (`assistant_conversation_behavior.md` §7: never invent a policy or capability that isn't actually present).
- If asked whether a specific action (e.g. "can I approve this expense right now") is possible, answer based on what this backend actually implements, not what the SDD describes as intended design.
- The Permission Matrix table itself is reproduced unchanged from the SDD; the enforcement-status notes beneath it are this document's own addition, clearly separated from the SDD's own content.

---

## Metadata

**Primary intents served:** Role Capabilities Q&A (primary); secondary support for Membership, Financial Operations, Faculty Questions, and Admin Questions when a question mixes "what am I allowed to do" with a status check.

**Related SQL tables:** `users`, `club_memberships`, `committees`, `committee_memberships`, `budgets`, `expenses`, `club_creation_requests`

**Related system documents:** `assistant_conversation_behavior.md` (Sections 1, 2, 10), `dashboard_redundancy_map.md` (per-role dashboard locations)

**Related RAG documents:** `platform_getting_started.md` (summary-level role overview; this document supersedes it for role-specific depth), `membership_process_guide.md`, `financial_operations_guide.md`, `club_creation_governance_guide.md`

**Keywords:** role, permissions, permission matrix, RBAC, student, faculty advisor, student affairs office, dean of student welfare, system admin, system administrator, member, committee member, volunteer coordinator, event coordinator, secretary, treasurer, vice president, president, role_in_club, what can I do as, capabilities, allowed actions, restricted actions, who approves, who can manage

**Chunking Notes:**
- Suggested Chunk Boundaries: split at each H2 (`##`) role heading (one chunk per Platform Role, one per Club Role), plus separate chunks for the Permission Matrix section, the FAQ section (or per-question if the retriever's chunk size requires it), Common Mistakes, and Important Notes.
- Keep each individual role's block (Purpose through Permission Notes) intact as a single chunk where possible — splitting a role's Allowed/Restricted Actions from its Permission Notes would lose the backend-enforcement caveat that makes this document accurate rather than a restatement of SDD intent.
- Keep the "Backend-enforcement status, row by row" paragraph attached to the Permission Matrix table in the same chunk, or immediately adjacent — the table alone (without that paragraph) would imply the SDD's rows are all currently working features, which they are not.
