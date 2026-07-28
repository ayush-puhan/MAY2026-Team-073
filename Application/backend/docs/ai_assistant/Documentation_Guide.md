# Documentation Overview

This documentation package is the complete reference for the ClubConnect AI Assistant, the AI Services Module of the ClubConnect platform. It exists to give developers everything needed to implement the assistant's runtime pipeline correctly: what the assistant is designed to do, how it must behave, and what platform knowledge it can draw on.

The package is split into three categories — Architecture, System Documents, and RAG Documents — because each answers a different question and is maintained on a different cadence. Architecture answers "how is this system designed?" System Documents answer "how must the assistant behave?" RAG Documents answer "what does the assistant know about the platform?" Keeping these separate means a change to platform knowledge (e.g. a new workflow) never requires touching behavior rules, and a change to tone or refusal policy never requires touching platform knowledge.

# Folder Structure

- **Architecture/** — the finalized design of the whole AI Services Module. Everything else in this package implements decisions made there.
- **System_Documents/** — rules for assistant behavior, injected into every LLM call regardless of what the user is asking.
- **RAG_Documents/** — the retrieval corpus of platform process knowledge, retrieved only when the detected intent requires it.

This division mirrors the runtime distinction between "always loaded" (System Documents) and "conditionally retrieved" (RAG Documents), with Architecture sitting outside the runtime prompt entirely as the design reference the other two categories were built from.

# Architecture

The `Architecture/` folder contains `ClubConnect_AI_Architecture_V2.md` (placed manually into this structure). It is the finalized design of the AI Services Module: the intent catalog, the module's frontend/backend design, the SQL-vs-RAG routing decisions, the workflow diagrams, and the module integration points across Student, Club Operations, Treasurer, Faculty, and University Administration.

It is the **source of truth** for the AI system because every System Document and every RAG Document was derived from decisions made in it — the intent catalog it defines is what `assistant_conversation_behavior.md` routes against, and the module boundaries it defines are what determined which RAG documents exist. Architecture is not modified to fit the other documents; the other documents are written to be consistent with it.

# System Documents

System Documents are always injected into every LLM call. They are kept small and rule-dense rather than explanatory, since their cost is paid on every single request regardless of intent.

## assistant_conversation_behavior.md

- **Purpose:** Defines the assistant's core behavior — identity, scope, tone, refusal policy, follow-up strategy, escalation rules, hallucination prevention, SQL-vs-RAG routing, dashboard narration rules, safety rules, and formatting rules.
- **Why it exists:** Every other behavior document assumes this baseline is already active. It is the single place that defines what the assistant is, what it will and won't do, and how it communicates.
- **When it is used:** On every request, without exception.
- **How the AI uses it during runtime:** It is loaded into the prompt on every call. The model uses Section 8 to decide whether to expect SQL context, RAG chunks, or both for the current intent, and uses Section 6 to decide whether to emit an `escalate: true` flag for the Response Formatter.

## recommendation_logic_playbook.md

- **Purpose:** Defines how club and event recommendations are produced — the signal inputs, the ranking philosophy, the academic-year guardrail, explanation strategy, and cold-start handling.
- **Why it exists:** Recommendation quality depends on consistent reasoning over the same signals every time; this document prevents the model from inventing ad hoc weighting schemes per request.
- **When it is used:** Always injected, but only load-bearing for Club Recommendation and Event Recommendation intents.
- **How the AI uses it during runtime:** When the SQL Context Builder supplies a recommendation feature summary (interests, memberships, history, academic year), the model applies this document's ranking and rationale rules to produce output; for all other intents it sits inactive in context.

## dashboard_redundancy_map.md

- **Purpose:** Maps, per role, which figures and lists already exist on a dashboard view, and specifies when the assistant should redirect versus narrate a synthesis.
- **Why it exists:** Without this map, the assistant would tend to restate raw data the user can already see, which is low-value and clutters conversational responses.
- **When it is used:** Always injected, most load-bearing for Navigation, Faculty Questions, and Admin Questions intents.
- **How the AI uses it during runtime:** Before generating any response containing a number, list, or status, the model checks this document's tables to decide between a redirect, a narrated summary, or a full direct answer.

# RAG Documents

RAG Documents are retrieved on demand — only the specific document(s) relevant to the detected intent are pulled into the prompt. None of them contain live data; each is pure platform process knowledge and is combined with SQL context only when the intent calls for both.

## platform_getting_started.md

- **Purpose:** Onboarding, platform-vs-club-scoped roles, sign-in, verification, navigation, and per-role capabilities.
- **Questions it answers:** "What is ClubConnect," "where do I find X," "what can a treasurer/faculty advisor do," "do I need to verify my email."
- **Knowledge provided:** General platform orientation and role-capability knowledge — no personal data.
- **SQL combination:** Used independently; navigation and role-capability questions do not require SQL context.

## membership_process_guide.md

- **Purpose:** How joining a club works — application, review, status lifecycle, club-scoped roles, committees, leaving a club.
- **Questions it answers:** "How do I join a club," "why was my application rejected," "what does 'withdrawn' mean," "can I join a committee."
- **Knowledge provided:** The application-to-membership process and status semantics.
- **SQL combination:** Combined with SQL context for personalized status questions ("why is my application still pending"); used independently for generic process questions ("how does club membership review work").

## event_lifecycle_guide.md

- **Purpose:** How events work — creation, registration, multi-session structure, check-in/attendance, volunteer assignments, external participants.
- **Questions it answers:** "How do I register for an event," "what happens if an event is full," "how does check-in work," "what's a missed volunteer assignment."
- **Knowledge provided:** Event registration and attendance process knowledge.
- **SQL combination:** Combined with SQL context for a user's own registration/attendance status; used independently for general process questions.

## rewards_system_guide.md

- **Purpose:** How points are earned, how balance is calculated, task completion, and the redemption process.
- **Questions it answers:** "How is my balance calculated," "can I lose points I've earned," "what happens if my redemption is rejected."
- **Knowledge provided:** Rewards mechanics — the ledger model, task/store catalogs, redemption workflow.
- **SQL combination:** Combined with SQL context when explaining a user's specific balance or ledger; used independently for general mechanics questions.

## club_creation_governance_guide.md

- **Purpose:** How a new club proposal is reviewed and approved, and how club lifecycle status (active/suspended/archived) works afterward.
- **Questions it answers:** "How do I propose a new club," "what happened to my proposal," "what does 'archived' mean for a club."
- **Knowledge provided:** Club creation and governance process knowledge, distinct from joining an existing club.
- **SQL combination:** Combined with SQL context for a user's own proposal status; used independently for general governance process questions.

## helpdesk_support_guide.md

- **Purpose:** How support tickets work (raising, threading, resolution), and how emergency reporting is handled as a distinct, always-escalated path.
- **Questions it answers:** "How do I raise a support ticket," "what's the difference between a ticket and an emergency report," "can I report anonymously."
- **Knowledge provided:** Support and emergency-reporting process knowledge.
- **SQL combination:** Combined with SQL context for a user's own ticket status; the emergency-reporting section is used independently and is never resolved conversationally regardless of context — it triggers Section 6 of `assistant_conversation_behavior.md`.

## financial_operations_guide.md

- **Purpose:** How club budgets and expense claims work, including the embedded (non-separate-table) expense approval model.
- **Questions it answers:** "How do I submit an expense," "is expense approval a separate table," "can a budget's expenses exceed its allocation process."
- **Knowledge provided:** Club-level financial process knowledge, role-filtered to treasurer/faculty contexts.
- **SQL combination:** Combined with SQL context for a specific club's actual budget/expense figures; used independently for general process questions. Never retrieved into a student-role context per the role-filtering rule in `assistant_conversation_behavior.md` Section 8.

# AI Request Flow

```
User Message
   ↓
Intent Detection
   ↓
Authorization
   ↓
SQL Context Builder
   ↓
RAG Retrieval
   ↓
Prompt Builder
   ↓
Gemini
   ↓
Response Formatter
   ↓
Final Response
```

1. **User Message** — the raw input from the user, arriving with the authenticated session already attached.
2. **Intent Detection** — the message is classified against the architecture's intent catalog (e.g. Club Recommendation, Application Status, Financial Operations).
3. **Authorization** — the detected intent is checked against the user's platform role and any club-scoped role; unauthorized intents (e.g. a student requesting financial data for a club they don't manage) are rejected before any data is fetched.
4. **SQL Context Builder** — for intents requiring personal or aggregate data, authorized, role-scoped, pre-summarized SQL context is built (e.g. "3 upcoming registered events," not raw rows).
5. **RAG Retrieval** — for intents requiring process knowledge, the relevant RAG document chunk(s) are retrieved based on the intent and query content.
6. **Prompt Builder** — assembles the final prompt: the three System Documents (always), plus SQL context and/or RAG chunks as determined by steps 4–5.
7. **Gemini** — the assembled prompt is sent to the primary LLM provider (with Groq/OpenRouter as configured fallbacks).
8. **Response Formatter** — applies formatting rules, reads any `escalate: true` flag and routes it to Helpdesk ticket creation, and appends the AI-generated disclaimer where required.
9. **Final Response** — delivered to the user through the relevant UI surface (chat window, recommendation cards, summary cards, etc.).

# Runtime Loading Strategy

- **Always-loaded documents:** All three System Documents (`assistant_conversation_behavior.md`, `recommendation_logic_playbook.md`, `dashboard_redundancy_map.md`) are injected into every single LLM call, regardless of detected intent.
- **Retrieved-on-demand documents:** RAG Documents are retrieved selectively — only the document(s) matching the current intent and query are pulled in. A navigation question never pulls in `financial_operations_guide.md`; a financial question is additionally never retrieved for a student-role context.
- **SQL context:** Built per-request for intents that need personal or aggregate data, already scoped to the authenticated user's authorization and pre-summarized before reaching the prompt.
- **What is NOT loaded:** The Architecture document is never injected into the runtime prompt — it is a development-time reference only. Raw, unsummarized database rows are never loaded. Financial RAG content is never loaded into a non-treasurer/faculty context.
- **Why evaluation documents are excluded from runtime:** Evaluation material (test cases, expected-response examples) exists to validate the assistant offline, not to inform live responses. Loading evaluation content into the runtime prompt would risk the model pattern-matching to test phrasing rather than reasoning from the actual System and RAG Documents, and would waste prompt budget on content with no runtime purpose.

# Future Development

Remaining implementation work, in dependency order:

1. **Intent Router** — implement classification against the architecture's intent catalog; this gates every downstream step.
2. **SQL Context Builder** — implement per-intent, role-scoped, pre-summarized data fetches from the schema described in `ClubConnect_Schema_Reference.md`.
3. **RAG Retriever** — implement retrieval over the `RAG_Documents/` corpus, chunked per each document's Chunking Notes.
4. **Prompt Builder** — implement assembly of System Documents + SQL context + RAG chunks into the final prompt sent to the LLM.
5. **Gemini Integration** — implement the primary LLM call with Groq/OpenRouter as configured fallback providers, per the architecture's provider abstraction requirement.
6. **Evaluation Suite** — build the offline test suite validating responses against the System and RAG Documents; this is intentionally the last step since it validates the pipeline above rather than being part of the runtime path.

# Maintenance Guidelines

- **Never mix SQL data into RAG documents.** RAG Documents must remain pure platform-knowledge references; live figures, names, and counts always come from the SQL Context Builder at runtime, never from a hardcoded RAG document.
- **Keep System Documents concise.** They are paid for on every single request; avoid expanding them with explanatory prose that belongs in a RAG document instead.
- **Preserve terminology.** Use the exact table, column, status, and role names from `ClubConnect_Schema_Reference.md` consistently across all documents so retrieval and model reasoning stay grounded in the actual schema.
- **Avoid duplicate knowledge across RAG documents.** Each concept should have exactly one authoritative home; other documents should reference it rather than re-explain it (as this corpus already does, e.g. financial and governance guides referencing role-based membership concepts rather than restating them).
- **Add new RAG documents only for new workflows.** A new platform workflow gets its own new RAG document following this same structure (Purpose, Overview, Definitions, workflow steps, FAQ, Common Mistakes, Edge Cases, Best Practices, Important Notes, Metadata); do not retrofit unrelated knowledge into an existing document just to avoid creating a new file.
