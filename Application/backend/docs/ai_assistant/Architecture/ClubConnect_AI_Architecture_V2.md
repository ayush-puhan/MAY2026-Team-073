# ClubConnect AI Assistant — Architecture V2 (Production-Ready Revision)

This revises the V1 architecture in place. Nothing here is a rewrite from zero — every change below references the specific V1 decision it's correcting. V2 stays SQL-first, lightweight-RAG, no orchestration framework, Gemini free tier throughout.

* * *

## Task 1 — Critical Review of V1

### 1.1 Weak areas in V1

| # | Weakness | Why it matters | Fix in V2 |
| --- | --- | --- | --- |
| 1 | **No explicit "Navigation" intent** | V1 folded navigation into "Getting Started," but navigation questions ("where do I find X") recur for _experienced_ users too, not just new ones — different SQL needs (none) and different tone (terse, not onboarding-style) | Split into its own intent in the Task 2 catalog, still served by Doc 1 |
| 2 | **Role-capabilities-matrix (Doc 7) was doing two jobs at once** | It mixed "what can this role do" (a RAG-worthy explainer) with "what should the assistant avoid re-answering because it's on the dashboard" (a behavioral rule) | Split: the dashboard-redundancy rule moves into the always-injected system prompt (Task 4); Doc 7 keeps only the plain-English capability explanation, and shrinks to ~0.5 doc-equivalent by being merged into Doc 1 (see 1.2) |
| 3 | **Financial-operations-guide (Doc 8) was under-used** — narrowest audience, but full retrieval weight | A rarely-hit document still costs the same embedding/index space and still competes in every similarity search, even for students who will never ask about it | Keep as RAG but mark `role_filter: [treasurer, faculty]` in metadata so it's excluded from the retrieval candidate set for students entirely (cost optimization, see Task 8) |
| 4 | **No handling for "ambiguous role-crossing" questions** — e.g. a Club Leadership user asking a Membership question | V1's SQL Context Mapping table was written per-intent assuming a single dominant role, but Club Leadership needs both the Student-style membership guide _and_ Ops-style answers | V2's Task 2 catalog stops binding intents to roles; intent detection and role-based SQL scoping are now fully orthogonal (any role can hit any intent; only the SQL scope changes) |
| 5 | **"Escalate to Helpdesk" was stated as a rule but never given a mechanism** | Without a concrete trigger, "escalate" is just a vibe, not an implementable behavior | V2 defines an explicit escalation signal set in Task 4 and Task 7 (stage: Response Formatter checks for an `escalate: true` flag the LLM is instructed to emit) |

### 1.2 Unnecessary complexity to remove

-   **10 documents was one too many.** Doc 7 (role-capabilities-matrix) is thin enough (0.5–1 page) that it doesn't earn a separate embedding/retrieval slot — its content is short, static, and almost always needed _alongside_ Doc 1 (Getting Started) rather than instead of it. **Merge Doc 7 into Doc 1.** This drops RAG documents from 8 to 7 without losing content.
-   **Doc 9 and Doc 10 were correctly identified as system-prompt material in V1** — that decision holds and V2 keeps it. No change needed there; it's confirmed as good design, not complexity to remove.
-   **The V1 "Conversation Strategy" table (Section 6) and the "SQL Context Mapping" table (Section 3) overlapped ~40%** — both were describing when to use SQL vs RAG, from two different angles. V2 folds both into the single Task 2 catalog below, which is the authoritative source going forward. (The Role Awareness and Recommendation Strategy sections from V1 remain distinct concepts and are preserved, refined in Task 6.)

### 1.3 Documents that become permanent system prompts instead of RAG

Already correct in V1 (Docs 9, 10) — V2 adds nothing new here, but see Task 4 for the _full_ always-injected block, which is broader than just these two documents (it also includes small structured facts like the role-dashboard-redundancy rule pulled out of old Doc 7).

### 1.4 Net document count after Task 1

**V1: 10 documents (8 RAG + 2 system) → V2: 9 documents (6 RAG + 3 system).**

The third system document is new: a compact **"dashboard redundancy map"** (which numbers/lists live on which dashboard, per role) extracted from old Doc 7. It's structured data (a lookup table), not prose, so it belongs in the system prompt rather than as an embedded RAG chunk competing for semantic relevance.

### 1.5 Cost-reduction opportunities identified

1.  Fewer RAG docs (7→6 embeddable, see 1.1/1.2) means a smaller vector index and fewer candidates per similarity search.
2.  Role-based metadata filtering (Task 8) means a given query only ever searches against a relevant subset, not the whole index — cutting both retrieval latency and the token cost of irrelevant chunks sneaking into context.
3.  Moving static/structured facts (role-dashboard map, behavior rules) to the system prompt avoids paying _retrieval_ cost for information that's needed on 100% of calls anyway — retrieval only pays off for information needed on a _minority_ of calls.
4.  SQL-only intents (status checks, balances) should **never trigger a RAG call at all** — this was implied in V1 but not enforced in the flow; V2 makes it an explicit gateway decision (Task 7).

* * *

## Task 2 — Intent → SQL → RAG → Prompt Flow Catalog

This table is the implementation blueprint for the AI Gateway's routing logic. "Always Injected System Documents" refers to the 3 system-prompt documents from Task 1.4, which are loaded on _every_ call regardless of intent — they're listed per row only to show which specific rules within them are most load-bearing for that intent.

| Intent | Description | Required SQL Tables | Required RAG Docs | Always-Injected Docs Used | SQL? | RAG? | Both? | Prompt Template Strategy | Expected Response Type | Example Questions | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Getting Started** | New/returning user orientation, what ClubConnect does | `users`, `student_profiles` | Doc 1 | Behavior rules | ✅ | ✅ | ✅ | System prompt + role/verification flag + Doc 1 excerpt | Short, friendly orientation, tailored to verification state | "What is this app?" "I just signed up, now what?" | P0 |
| **Navigation** | "Where do I find X" for existing users | `users.role` (for menu tailoring) | Doc 1 | Dashboard redundancy map | ✅ | ✅ | ✅ | Terse: role + Doc 1 nav section only, no onboarding tone | One-line direction to the right screen | "Where do I see my tickets?" "How do I get to the calendar?" | P0 |
| **Club Discovery** | Browsing/searching clubs by category, name, keyword | `clubs`, `club_interests` | Doc 1 (brief) | — | ✅ | — | — | SQL results formatted as a list; RAG only if user asks "what does this club do" beyond the DB description | List of matching clubs with short DB-sourced descriptions | "Show me tech clubs" "Is there a chess club?" | P0 |
| **Club Recommendation** | Personalized suggestions | `user_interests`, `club_interests`, `club_memberships`, `student_profiles.academic_year` | Recommendation Playbook (system) | Recommendation Playbook | ✅ | — | — | SQL feature summary → LLM reasoning per playbook, no RAG doc needed | 2–5 ranked clubs, each with a one-line evidence-based rationale | "Recommend clubs for me" "What matches my interests?" | P0 |
| **Event Recommendation** | Personalized event suggestions | `events`, `event_interests`, `event_registrations`, `attendance_records`, `club_memberships` | Recommendation Playbook (system) | Recommendation Playbook | ✅ | — | — | Same pattern as Club Recommendation | 2–5 ranked upcoming events with rationale | "What events should I attend?" "Any workshops I'd like?" | P0 |
| **Membership Process (how it works)** | Explaining the general apply→approve flow | — | Doc 2 | — | — | ✅ | — | RAG only, no personal data needed | Generic process explanation | "How do I join a club?" "What happens after I apply?" | P0 |
| **Application Status** | User's specific application state | `club_join_applications` | Doc 2 (only if user also asks "why"/"what next") | — | ✅ | optional | optional | SQL result first; RAG only if explanation of next steps is also requested | Direct status + optional next-step explanation | "Did I get into Robotics Club?" "Is my application still pending?" | P0 |
| **Event Registration (how it works)** | Explaining registration/check-in mechanics | — | Doc 3 | — | — | ✅ | — | RAG only | Generic mechanics explanation | "How do I register for an event?" "How does check-in work?" | P1 |
| **Attendance** | User's own attendance record | `attendance_records`, `event_registrations` | Doc 3 (only if asked "how is attendance tracked") | — | ✅ | optional | optional | SQL first | Direct record of attended/registered events | "Did I get marked present at the hackathon?" | P1 |
| **Rewards** | Points system mechanics + personal balance | `reward_points_ledger`, `reward_task_completions`, `reward_redemptions` | Doc 4 | — | ✅ | ✅ | ✅ | Doc 4 mechanics + SQL balance/ledger summary | Explanation + current points/progress | "How do reward points work?" "How many points do I have?" | P1 |
| **Announcements** | What's new / how announcements work | `announcements` (scoped to user's clubs) | Doc 1 (nav section) | — | ✅ | optional | optional | Recent rows formatted as a digest | Summary of recent announcements + pointer to full Announcement Center | "Any new announcements?" "What did the Robotics club post?" | P1 |
| **Club Creation & Governance** | Proposing a new club, tracking a proposal | `club_creation_requests` | Doc 5 | — | ✅ | ✅ | ✅ | Doc 5 process + SQL status of user's own request(s) | Process explanation + specific status if applicable | "How do I start a new club?" "Is my club proposal approved yet?" | P2 |
| **Support Tickets** | Raising/tracking a helpdesk ticket | `support_tickets`, `ticket_responses` | Doc 6 | Escalation rules | ✅ | ✅ | ✅ | Doc 6 process + SQL ticket status | Process explanation + specific ticket status | "How do I report a bug?" "Is my ticket resolved?" | P0 |
| **Emergency Reporting** | Harassment/safety/medical reports | `emergency_reports` (write path only, never conversational resolution) | Doc 6 (emergency section) | Escalation rules | — | ✅ | — | **Never LLM-resolved** — detect intent, surface the Emergency Report action immediately, minimal generation | Directive: "Use the Emergency Report button now" + brief reassurance, no advice-giving | "Someone is harassing me at this event" | **P0 — safety-critical** |
| **Financial Operations (Treasurer)** | Budget/expense process + own club's figures | `budgets`, `expenses` | Doc 8 (role-filtered) | — | ✅ | ✅ | ✅ | Doc 8 process + aggregated (not raw) SQL summary | Process explanation + high-level figure narration | "How do I submit an expense?" "What's our budget utilization?" | P2 |
| **Faculty Questions** | Oversight of advised clubs | `clubs.faculty_advisor_id`, pending `events`/`expenses` | Doc 3 + Doc 8 (role-filtered) | Dashboard redundancy map | ✅ | ✅ | ✅ | SQL pending-approval counts + relevant process doc excerpts | Narrative summary supporting the approval dashboard | "What events are waiting on my approval?" | P2 |
| **Admin Questions** | Platform-wide oversight, club approvals | `club_creation_requests`, aggregate counts | Doc 5 + Doc 1 | Dashboard redundancy map | ✅ | ✅ | ✅ | Only engaged for synthesis beyond raw dashboard numbers | Narrative synthesis (e.g., "3 proposals this week, all in Arts category") | "Summarize this week's new club proposals" | P3 |
| **Profile & Account** | Editing profile, verification status, accessibility prefs | `users`, `student_profiles` | Doc 1 (account section) | — | ✅ | optional | optional | User's own row only | Guidance + current field values | "How do I change my profile photo?" "Am I verified yet?" | P1 |
| **Role Capabilities Q&A** | "What can I do as a Club Leader" | `users.role` | Doc 1 (merged capabilities section) | — | ✅ | ✅ | ✅ | Role + Doc 1 excerpt | Plain-English capability summary | "What can I do as Faculty Advisor?" | P2 |
| **Ambiguous Request** | Underspecified ask | varies | varies | Conversation behavior rules | — | — | — | One targeted clarifying question, or default to stored interests if available | Single follow-up question | "Show me clubs" (no criteria) | P1 |
| **Out-of-Scope / Refusal** | Off-topic, unauthorized data, homework help, etc. | none | none | Conversation behavior rules | — | — | — | Refusal template, no fabrication | Polite decline + redirect | "Do my calculus homework" "What's Priya's phone number?" | P0 |

* * *

## Task 3 — Knowledge Base Improvement Decisions

| Document (V1 name) | Decision | Reasoning |
| --- | --- | --- |
| 01 platform-getting-started.md | **Keep + Merge in** old Doc 7 | Becomes the single "orientation + navigation + role capabilities + account basics" reference — all short, static, cross-role content that's cheap to always have available |
| 02 membership-process-guide.md | **Keep as-is** | Highest-frequency intent, correctly scoped, no overlap with anything else |
| 03 event-lifecycle-guide.md | **Keep as-is** | Same reasoning as Doc 2 |
| 04 rewards-system-guide.md | **Keep as-is** | Self-contained, no overlap |
| 05 club-creation-governance-guide.md | **Keep as-is** | Low frequency but distinct enough to justify its own doc rather than force-merging into Doc 2 |
| 06 helpdesk-support-guide.md | **Keep, but split internally into two clearly-headed sections** (Support Tickets / Emergency Reporting) within the _same file_ — not two files | The two flows share audience and tone but have wildly different response strategies (Task 2), so the LLM needs the section boundary to be unambiguous even though one embedding-worthy document is enough |
| 07 role-capabilities-matrix.md | **Delete as standalone; merge into Doc 1** | Too thin to be its own retrieval unit (see Task 1.2) |
| 08 financial-operations-guide.md | **Keep, add `role_filter` metadata** | Correct content, wrong retrieval scope in V1 — narrowest-audience doc needs to be excluded from broad searches, not deleted |
| 09 recommendation-logic-playbook.md | **Keep as system prompt (unchanged from V1)** | Confirmed correct in Task 1 |
| 10 assistant-conversation-behavior.md | **Keep as system prompt, expand slightly** to include the concrete escalation-signal mechanism from Task 1.1 #5 | Closes the gap between "should escalate" and "how the code knows to" |
| _(new)_ dashboard-redundancy-map | **Add as a third system document** | Structured lookup data, not prose — belongs in system prompt, not RAG, per Task 1.4 |
| _(new)_ response\_examples.md | **Add as an internal training/eval asset, not a runtime document at all** | Never loaded into any prompt; used only for prompt-engineering QA and regression testing (see deliverable) |

**Net result: 6 RAG documents, 3 system-prompt documents, 1 offline eval document.**

```
knowledge_base/
├── rag/
│   ├── 01_platform_getting_started.md      (merged: onboarding + nav + roles + account)
│   ├── 02_membership_process_guide.md
│   ├── 03_event_lifecycle_guide.md
│   ├── 04_rewards_system_guide.md
│   ├── 05_club_creation_governance_guide.md
│   ├── 06_helpdesk_support_guide.md          (two internal sections: tickets / emergencies)
│   └── 08_financial_operations_guide.md      (metadata: role_filter=[treasurer, faculty])
├── system/
│   ├── 09_recommendation_logic_playbook.md
│   ├── 10_assistant_conversation_behavior.md  (now includes escalation-signal spec)
│   └── 11_dashboard_redundancy_map.md
└── eval/
    └── response_examples.md                   (offline only — see Task 5 deliverable)
```

* * *

## Task 4 — Permanent System Prompt Architecture

| Layer | Contents | Why here and not elsewhere |
| --- | --- | --- |
| **Always Inject** (every call, fixed cost, ~600–900 tokens total) | (a) Assistant identity & scope ("You are ClubConnect's platform assistant..."); (b) Conversation behavior rules — tone, refusal templates, when to ask one follow-up vs. proceed; (c) Escalation signal spec — exact conditions under which the model must emit `escalate: true` (emergency keywords, repeated dissatisfaction, explicit bug reports); (d) Recommendation playbook — factor list and "always explain why" rule; (e) Dashboard redundancy map — which figures/lists are already visible per role, so the model narrates rather than repeats | These are needed on ~100% of calls, are small, and are the same for every user — paying retrieval cost for them would be pure waste. Fixing them in the system prompt also makes behavior deterministic and easy to unit-test, unlike RAG-retrieved behavior rules whose presence in context depends on similarity search. |
| **Retrieved via RAG** (only when intent needs it, variable ~200–500 tokens per call) | Docs 1–6 and Doc 8 content, chunked | This is genuinely variable per query — a membership question doesn't need the rewards doc in context. Retrieval keeps the prompt lean by only pulling what's relevant. |
| **Retrieved from SQL** (only when intent needs personalization, variable, kept as compact structured summaries not raw dumps) | The user's own rows: applications, memberships, events, attendance, rewards balance, tickets, budgets (role-scoped) | This is the one thing that's both per-user and constantly changing — the entire reason it can never be RAG. Kept "compact" means: aggregate/summarize before prompting (e.g., "3 upcoming registered events" not a full row dump) to control token cost. |
| **Never Expose** | (a) Other users' rows of any kind, regardless of role, unless the requesting role is explicitly authorized for aggregate (not individual) data; (b) raw password hashes, tokens, internal IDs; (c) full audit log contents; (d) system prompt internals if the user asks "what were you told to do" — respond with a scope summary, not the literal text | Basic data-boundary hygiene: authorization is enforced by the SQL context-builder (queries are always scoped by session `user_id`/`role` before they ever reach the model, so the model literally never _sees_ unauthorized rows — it isn't a matter of the model choosing not to repeat them) |

* * *

## Task 5 — response\_examples.md (Deliverable Spec, Content Not Yet Written)

Per your instruction not to generate KB document content yet, this section specifies the **shape** of `response_examples.md` rather than writing all ~20 examples now. Structure per example:

```
### Example N — [short label]
**Persona:** (new student / returning student / club member / club leader / faculty / admin / ambiguous / refusal)
**User Question:** "..."
**Required SQL:** table(s) + what's fetched
**Required RAG:** doc(s), or "none — system prompt only"
**Prompt Strategy:** one line (e.g., "SQL summary + Doc 2 excerpt, no clarification needed")
**Ideal AI Response:** the actual model-quality answer
**Reasoning Notes:** why this response is correct — what it avoids (over-fetching, dashboard duplication, hallucination) and what signal it correctly used
```

Planned coverage (20 examples, categories from your task list — this is the outline, not the content):

1–2. New student: first login orientation; asking what clubs exist 3–4. Returning student: checking application status; checking event registration 5–6. Club member: asking how rewards work + own balance; asking about own attendance 7–8. Club leader: reviewing pending applications guidance; asking about club's budget 9–10. Faculty advisor: pending event approvals; general oversight question 11–12. Administrator: club proposal summary; platform-wide question requiring refusal (out of admin's intended AI scope, e.g. "give me every student's email") 13–14. Recommendation requests: club recommendation with mixed signals (stated interest vs. attendance history); event recommendation for a final-year student (showing academic year as _one_ factor, not a filter) 15–16. Support requests: routine ticket status check; a request that should escalate (repeated "this isn't working" complaints) 17. Event registration: capacity/waitlist edge case 18. Membership status: rejected application, tactful explanation 19. Ambiguous question: "tell me about clubs" with no stored interests yet (cold-start case) 20. Refusal example: request for another student's private data, and a homework-help request

This becomes the eval suite against which prompt changes are regression-tested before shipping.

* * *

## Task 6 — Recommendation Strategy (Refined)

Unchanged core principle from V1, confirmed: **no hardcoded rule tables, no fixed weighting formula.** Refinements for V2:

-   **Signal inputs, explicitly not ranked as a rigid priority order this time** (V1 implied strict ordering — that itself risks becoming a de facto hardcoded rule): explicit interests (`user_interests` ↔ `club_interests`/`event_interests`), current memberships (exclusion + affinity), behavioral history (`event_registrations`, `attendance_records`), and academic year (`student_profiles.academic_year`) are all handed to the model as parallel evidence in a single feature summary — the model weighs them contextually per request rather than the pipeline pre-ranking them.
-   **Explicit guardrail added in V2:** the playbook must state outright — _"Academic year is contextual color, never a filter or a default assumption. Never state or imply a rule like 'final-year students should prefer X.' If academic year is used in a rationale, it must be combined with at least one other signal (interest or history), never cited alone."_ This directly satisfies your instruction and closes a gap V1 left implicit.
-   **Every recommendation must carry a one-line, evidence-cited rationale** (unchanged from V1) — output is rejected/regenerated by the Response Formatter (Task 7) if a recommendation lacks a rationale referencing an actual signal.
-   **Cold-start handling (new in V2):** if a student has no `user_interests` and no history, the assistant asks one clarifying question (interest area) rather than guessing — this case is explicit in `response_examples.md` (#19).

* * *

## Task 7 — AI Gateway Flow

```
                    User
                     │
                     ▼
            1. Intent Detection
                     │
                     ▼
           2. Authorization Check
                     │
                     ▼
         3. Determine SQL Context
                     │
                     ▼
         4. Determine RAG Context
                     │
                     ▼
            5. Retrieve SQL
                     │
                     ▼
          6. Retrieve Documents
                     │
                     ▼
            7. Prompt Builder
                     │
                     ▼
              8. Gemini API
                     │
                     ▼
          9. Response Formatter
                     │
                     ▼
                   Client
```

| Stage | What happens | Notes |
| --- | --- | --- |
| **1\. Intent Detection** | Lightweight classification (a single small Gemini call with the intent list as a closed set, or a rule-based keyword/embedding match to keep it near-zero-cost) maps the message to one of the Task 2 intents | Kept intentionally simple — this is NOT a separate agent, just a routing step. A regex/keyword pre-filter can catch obvious cases (e.g., "recommend" → Club/Event Recommendation) before falling back to a classification call, saving tokens on the common case |
| **2\. Authorization Check** | Confirms the authenticated session's role can access this intent at all (e.g., a student cannot reach "Admin Questions") | Pulled from the existing Auth/session layer — no new auth system, just a gate before any DB access happens |
| **3\. Determine SQL Context** | Looks up, per Task 2's table, which tables/columns this intent needs, scoped by `user_id`/`role` | Pure lookup against the catalog — deterministic, no LLM call needed |
| **4\. Determine RAG Context** | Looks up which doc(s) (if any) this intent needs, applying role-based metadata filters (e.g., Financial doc excluded for students) | Also a deterministic lookup, not an LLM decision — keeps cost and behavior predictable |
| **5\. Retrieve SQL** | Executes the scoped query/queries, then **summarizes/aggregates before prompting** (never dumps raw rows) | This is the step most responsible for controlling token cost — a `SELECT *` dump of 40 attendance rows is far more expensive than "attended 6 of 8 registered events this semester" |
| **6\. Retrieve Documents** | If intent requires RAG, runs a similarity search restricted to the metadata-filtered subset, returns top-k chunks (k tuned in Task 8) | Skipped entirely for SQL-only intents (status checks, balances) — this is the explicit enforcement called out in Task 1.5 #4 |
| **7\. Prompt Builder** | Assembles: always-inject system block + retrieved SQL summary + retrieved RAG chunks + conversation history (trimmed) + user message | Single flat prompt — no multi-agent handoff, no LangGraph state machine, just template assembly |
| **8\. Gemini API** | Single completion call | One call per turn; recommendation/support flows do NOT require multiple chained calls |
| **9\. Response Formatter** | Parses the model's output for the `escalate` flag (Task 4), strips any accidental leakage patterns, appends the "AI-generated, verify on your dashboard" disclaimer where relevant, and routes escalation flags to the Helpdesk ticket creation flow | This is where the "escalate to Helpdesk" rule from Task 1.1 #5 actually becomes executable rather than aspirational |

No agent framework, no planning loop, no tool-calling chains — every request is one classification decision + one deterministic context lookup + one Gemini call + one formatting pass. This matches your "no multi-agent, no LangGraph" constraint exactly.

* * *

## Task 8 — Cost Optimization (Gemini Free Tier)

| Parameter | Recommendation | Reasoning |
| --- | --- | --- |
| **Max RAG documents** | 6 embeddable documents (see Task 3) | Small enough that even a full brute-force similarity search across all of them is cheap; no need for a heavier vector DB than SQLite-adjacent flat storage or a simple in-memory index |
| **Chunk size** | ~300–500 tokens per chunk, split by heading/section (not fixed character windows) | Your source docs are already short (1–3 pages) and structured with headings — heading-aligned chunking keeps each chunk semantically complete, avoiding the classic "half an answer in one chunk, half in the next" retrieval failure |
| **Metadata per chunk** | `doc_id`, `section_title`, `role_filter` (e.g., `[all]` or `[treasurer, faculty]`), `intent_tags` (from Task 2's catalog) | Enables the role-based pre-filtering from Task 1.5 #2 and lets retrieval skip irrelevant chunks before similarity scoring even runs |
| **Retrieval count (k)** | k=2–3 chunks per query | With only 6 short documents, you rarely need more than 2–3 chunks to fully cover a procedural question; higher k mostly adds noise/cost here, not accuracy |
| **Prompt size budget** | Target ~1,200–1,800 tokens total per call (system block ~700–900 + SQL summary ~100–300 + RAG chunks ~300–600 + trimmed history ~200) | Comfortably inside Gemini free-tier per-request limits with margin; keeps latency low too (your 10-second NFR) |
| **Caching opportunities** | (a) Cache the always-inject system block as a static string (no reason to reconstruct it per call); (b) cache embeddings for the 6 RAG docs at build/deploy time, not per-query; (c) cache a user's SQL summary within a single conversation turn if multiple intents are detected in one message, rather than re-querying | These are all "compute once, reuse" wins with zero architectural complexity added |
| **Embedding strategy** | Precompute embeddings for the RAG doc chunks once at deploy time (or on doc update); do **not** re-embed on every query — only the user's live message needs an embedding call at runtime | Cuts embedding API calls by roughly 6 documents' worth of chunks × however many queries per day down to just 1 embedding call per user query |
| **Token minimization** | (a) Summarize SQL results server-side in Python before they ever reach the prompt (never let the model see a raw multi-row JSON dump); (b) trim conversation history to the last 2–3 turns, not the full session; (c) skip RAG retrieval entirely for SQL-only intents (Task 2 marks these clearly); (d) skip intent-classification LLM calls where a cheap keyword match already resolves the intent unambiguously | Every one of these directly reduces either input or output tokens without touching answer quality |

**Bottom line:** with 6 RAG docs, k=2–3 retrieval, ~1,500-token average prompts, and skip-when-possible logic for both RAG and classification, a single conversation turn should sit comfortably within Gemini's free-tier request and token-per-minute limits even under moderate concurrent load — which matches your NFR of "support multiple concurrent AI requests" without requiring paid-tier headroom.

* * *

## Summary of What Changed (V1 → V2)

-   10 documents → **9** (7 RAG collapsed to 6 by merging role-capabilities into Getting Started; system docs grow from 2 to 3 by extracting the dashboard-redundancy map)
-   Intent-to-role binding removed — **intents and roles are now orthogonal**, with SQL scoping (not intent selection) handling role differences
-   Escalation went from a stated rule to an **implementable signal** (`escalate: true`) with a concrete Gateway stage that acts on it
-   Recommendation strategy tightened to explicitly forbid academic-year-only rationales, closing a gap the instructions specifically flagged
-   Added a full **Gateway flow diagram + stage-by-stage spec** (didn't exist in V1)
-   Added a full **cost-optimization spec** with concrete numbers (chunk size, k, token budget) — V1 only had qualitative principles
-   Added `response_examples.md` as a **new offline eval asset**, not a runtime document — scoped and outlined, content deferred per your instruction

Ready to proceed to writing actual document content once you confirm — recommended order unchanged in spirit from V1: behavior/escalation system prompt → Doc 2 (membership) → recommendation playbook → Doc 3 (events) → Doc 1 (merged getting-started).