# ClubConnect AI API Reference

**Base path:** `/api/ai`
**Backend source of truth:** `ClubConnect_Backend_Phase6B_stabilized.zip` — every claim below was verified against `app/modules/ai_services/routes.py`, `intent_router.py`, `cache.py`, `report_service.py`, `analytics_service.py`, and `content_service.py`, and cross-checked against the supplied test evidence (`apitesting.txt`, `ai_api_responses.json`, and the project's own `AI_API_REFERENCE.md`/`TEST_REPORT.md`/`CHANGELOG.md`).

---

## 1. Base Information

- **Purpose:** the ClubConnect Assistant — a role-aware AI layer over the platform providing conversational Q&A (`/chat`), narrative report generation (`/reports`), financial/performance analytics (`/analytics/*`), and short draft-content generation (`/content`).
- **Authentication:** every endpoint except `GET /ai/health` requires a Bearer JWT, obtained from `POST /api/auth/login` (or the OTP/Google flows), sent as `Authorization: Bearer <access_token>`. The token must also correspond to an active row in the server-side session table — a structurally valid but revoked/logged-out JWT still gets a `401`.
- **Common headers:**
  - `Authorization: Bearer <token>` (all endpoints but `/health`)
  - `Content-Type: application/json` (all `POST` endpoints)
- **Common request format:** all `POST` endpoints take a JSON body (even `/analytics/financial` and `/analytics/performance`, which take no fields — send `{}`).
- **Common response envelope:** every successful response includes `"status": "ok"`. Gemini-failure responses use `"status": "ai_unavailable"` with HTTP `503`.

---

## 2. Endpoint / Feature Index

| Feature | Endpoint | Method | Roles | Purpose |
|---|---|---|---|---|
| Health/config check | `/ai/health` | GET | Public (no auth) | Confirms Gemini + knowledge base wiring |
| AI Chat | `/ai/chat` | POST | All authenticated (per-intent authorization) | Conversational Q&A across 22 intents |
| Report Generation | `/ai/reports` | POST | All authenticated (per-report-type authorization) | 9 narrative report types |
| Financial Analytics | `/ai/analytics/financial` | POST | Treasurer, Faculty Advisor, Student Affairs Office, Dean of Student Welfare, System Admin | Budget/expense analytics + chart data |
| Performance Analytics | `/ai/analytics/performance` | POST | All authenticated (role-orthogonal, auto-scoped) | Engagement/performance analytics + chart data |
| Content Generation | `/ai/content` | POST | All authenticated | Drafts announcements, invitations, etc. |

---

## 3. AI Chat / Intent-Based APIs

**Route:** `POST /api/ai/chat`
**Request body:** `{ "message": "<free text, non-empty after trim>" }`
**Response shape (all intents):**
```json
{
  "status": "ok",
  "authorized": true,
  "detected_intent": "Membership",
  "response": "<Gemini's natural-language answer>",
  "sql_context": { "...": "intent-specific, or null" },
  "rag_context": [ { "doc_id": "...", "section_title": "...", "text": "..." } ],
  "cache_hit": false,
  "user_context": { "user_id": 2, "full_name": "User 2", "role": "student" }
}
```
- `detected_intent` is a keyword-pre-filter match against the catalog below, falling back to a Gemini classification call only when the keyword pass can't resolve it, and finally to `"Ambiguous Request"` if nothing fits.
- `authorized: false` means the intent was recognized but this user's role doesn't grant it — **this is still an HTTP `200`**, not a `403`. `sql_context` is `null` in that case; `rag_context` may still be populated so the assistant can give a generic, non-personalized answer, and `response` carries a fixed decline message ("I can't help with that — that's outside what I have access to here...").
- `sql_context` is `null` for RAG-only intents (pure process/orientation explanations) — normal, not a bug.

### Intent catalog (all 22)

Every intent shares the one route/request/response shape above — what differs per intent is **RBAC** and whether the answer is cacheable. Unless noted otherwise below, an intent is **role-orthogonal**: any authenticated role may reach it, and personalization/visibility is handled by scoping the SQL context to the caller's own data, not by blocking the intent itself.

| Intent | RBAC | Cacheable |
|---|---|---|
| Emergency Reporting | Every role, always — safety-first; never blocked | No |
| Getting Started | Role-orthogonal | **Yes** |
| Navigation | Role-orthogonal | **Yes** |
| Club Discovery | Role-orthogonal | No |
| Club Recommendation | Role-orthogonal | **Yes** |
| Event Recommendation | Role-orthogonal | **Yes** |
| Membership Process | Role-orthogonal | **Yes** |
| Application Status | Role-orthogonal | No |
| Membership | Role-orthogonal | **Yes** |
| Event Registration | Role-orthogonal | **Yes** |
| Attendance | Role-orthogonal | **Yes** |
| Rewards | Role-orthogonal | No |
| Announcements | Role-orthogonal | No |
| Club Creation & Governance | Role-orthogonal | No |
| Support Tickets | Role-orthogonal | No |
| **Financial Operations** | Faculty Advisor (platform role), **or** club-scoped Treasurer (any platform role) | No |
| **Faculty Questions** | Faculty Advisor only | No |
| **Admin Questions** | Student Affairs Office, Dean of Student Welfare, System Admin only | No |
| Profile & Account | Role-orthogonal | **Yes** |
| Role Capabilities Q&A | Role-orthogonal | **Yes** |
| Ambiguous Request | n/a (fallback intent, never authorized-gated) | No |
| Out-of-Scope | n/a (fallback intent, never authorized-gated) | No |

### Role-gated intents in detail

**Financial Operations** — *"submit an expense", "our budget", "budget utilization", etc.*
Authorized for a **Faculty Advisor** (platform role) OR anyone holding a club-scoped **Treasurer** role (`club_memberships.role_in_club`) — including a platform-role `student` who is their club's treasurer. A plain student with no treasurer role gets `authorized: false` and the standard decline, which (per the actual refusal template) still names the clubs it *can* help with if the user has any club association — e.g. "*I can help you with financial status summaries for the Entrepreneurship Cell or Hackerspace, which are the clubs associated with your account, if that's useful.*" (verbatim, tested).

**Faculty Questions** — *"clubs I advise", "events waiting for approval"* — Faculty Advisor only.

**Admin Questions** — *"platform-wide engagement", "new club proposals"* — Student Affairs Office, Dean of Student Welfare, or System Admin only.

**Emergency Reporting** — reachable by *every* role unconditionally, but `sql_context` is always `null` — emergency content is never handed to the LLM for interpretation. The response text always instructs the user to use the in-app Emergency Report action, and the message body includes the literal marker `` `escalate: true` `` for the frontend to key off of and show an escalation UI. Verified against test evidence for `system_admin`, `student_affairs_office`, and `dean_student_welfare` roles — all three receive the identical fixed escalation response, not a personalized one.

**What the frontend should display/use:** render `response` as the assistant's message; use `detected_intent` only for debugging/telemetry (it's not a stable public contract per intent naming); treat a `false` `authorized` as a normal decline bubble, not an error state; show `rag_context`/`sql_context` only in a developer/debug view if at all.

---

## 4. Reports

**Route:** `POST /api/ai/reports`
**Request body:** `{ "report_type": "<key>" }`
**Response (authorized):**
```json
{
  "status": "ok",
  "report_type": "budget",
  "label": "Budget Report",
  "authorized": true,
  "data": { "...": "report-type-specific structured data" },
  "summary": "<AI-generated narrative>"
}
```
**Response (recognized type, not authorized):** same shape with `"authorized": false, "data": null, "summary": null` — HTTP `200`.
**Response (unrecognized `report_type`):** HTTP `400`, `{"status": "error", "message": "Unsupported report type.", "supported_report_types": [...]}`.

Exact catalog keys (do not alias or rename):

| `report_type` | Label | Supported roles | Example request | Notes |
|---|---|---|---|---|
| `student_activity` | Student Activity Report | Everyone (own data) | `{"report_type": "student_activity"}` | Memberships + attendance + rewards + open support tickets |
| `attendance` | Attendance Report | Everyone (own data) | `{"report_type": "attendance"}` | — |
| `membership` | Membership Report | Everyone (own data) | `{"report_type": "membership"}` | — |
| `reward` | Reward Report | Everyone (own data) | `{"report_type": "reward"}` | — |
| `support_ticket` | Support Ticket Report | Everyone (own data) | `{"report_type": "support_ticket"}` | — |
| `volunteer` | Volunteer Report | Everyone (own data) | `{"report_type": "volunteer"}` | — |
| `club_activity` | Club Activity Report | Everyone — scope-gated, not role-gated | `{"report_type": "club_activity"}` | A plain member with no officer role anywhere gets an honest **empty** result (`authorized: true`, empty club list), not a `403`. Officers get their own club(s); faculty get advised clubs; admin-tier gets platform-wide (university-scoped). |
| `budget` | Budget Report | Club **treasurer** (any club), **faculty advisor**, or admin-tier | `{"report_type": "budget"}` | Treasurer/faculty: own club(s) only. Admin-tier with no club of their own: platform-wide aggregate. **Confirmed by testing:** a `student`-role user who holds a club-scoped Treasurer role correctly receives budget data scoped to just their own treasurer club(s) — this was flagged as a possible RBAC leak during manual testing and investigated; it is intentional and correctly scoped (verified against `club_memberships`). |
| `emergency_summary` | Emergency Report Summary | Admin-tier only (System Admin / Student Affairs Office / Dean of Student Welfare) | `{"report_type": "emergency_summary"}` | Aggregate counts/category/status breakdown only — never a reporter identity or free-text incident description, even for authorized admin-tier callers. |

**Frontend interpretation:** distinguish a `400` (bad/unknown `report_type` — a client bug) from a `200` with `authorized: false` (a real, expected role limitation) — the two bodies are nearly identical, so check the HTTP status code, not just the `authorized` field.

---

## 5. Analytics

### Financial Analytics — `POST /api/ai/analytics/financial`
Request body: `{}` (no fields — fully scoped from the caller's identity).

**Authorized response:**
```json
{
  "status": "ok",
  "authorized": true,
  "summary": "<AI-generated explanation>",
  "analytics": { "clubs": [ { "club_name": "...", "total_allocated_amount": 91000.0, "total_expenses_claimed": 9550.0, "utilization_percent": 10.5, "...": "..." } ], "total_pending_approvals": 3 },
  "chart": { "type": "bar", "labels": ["Club A", "Club B"], "series": [ { "name": "Allocated", "values": [91000.0, 54000.0] }, { "name": "Claimed", "values": [9550.0, 5770.0] } ] }
}
```
**Not authorized:** `200`, `{"status": "ok", "authorized": false, "message": "You don't have access to financial analytics."}`.

**Role-based authorization:** club treasurer (any club — including a `student` platform role holding a club-scoped Treasurer role), Faculty Advisor, Student Affairs Office, Dean of Student Welfare, or System Admin. A plain member/student with no treasurer role is denied (still `200`, not `403`).

### Performance Analytics — `POST /api/ai/analytics/performance`
Request body: `{}`. **Role-orthogonal — every role gets a `200`, no denied state.** Scope is auto-resolved and returned in `"scope"`:

| Caller | `scope` value | What's returned |
|---|---|---|
| Admin-tier (`system_admin`/`student_affairs_office`/`dean_student_welfare`) | `"platform"` | Platform-wide (university-scoped) engagement overview |
| Faculty Advisor | `"advised_clubs"` | Their advised clubs' oversight data + club activity |
| Club officer (any officer-tier `role_in_club`) | `"led_clubs"` | Their led club(s)' activity snapshot |
| Plain student/member | `"personal"` | Their own club involvement, attendance, rewards |

**Frontend interpretation:** treat `scope` as a label to show, not a fixed enum to branch UI logic on beyond the four observed values — the underlying `analytics` shape genuinely differs per scope (see the code for exact field names per branch), so don't assume a fixed schema across scopes.

**Chart data (both analytics endpoints):** `{"type": "bar", "labels": [...], "series": [{"name": "...", "values": [...]}]}` — backend-computed, ready to hand to any bar-chart component. No forecasting/prediction in either endpoint — Gemini only writes the `summary` text; every number in `analytics`/`chart` is computed by the backend.

**Response `503` (both):** `{"status": "ai_unavailable", "message": "...", "analytics_type": "financial"|"performance"}`.

---

## 6. Content Generation

**Route:** `POST /api/ai/content`
**Request body:** `{ "content_type": "<key>", "details": "<optional free text>" }`
**Response:** `{"status": "ok", "content_type": "announcement", "label": "Announcement Draft", "draft": "<generated text>"}`

Every authenticated role may use every content type — this is intentional, not a gap. Nothing is ever persisted or sent; the frontend places the draft wherever it belongs (announcement form, email compose box, etc.).

| `content_type` | Label |
|---|---|
| `announcement` | Announcement Draft |
| `event_description` | Event Description |
| `club_description` | Club Description |
| `invitation` | Invitation Message |
| `volunteer_recruitment` | Volunteer Recruitment Message |
| `reminder` | Reminder Message |
| `approval_comment` | Approval Comment |
| `rejection_message` | Rejection Message |
| `budget_justification` | Budget Justification |
| `certificate_description` | Certificate Description |

**Behavior when `details` is missing/empty (tested, intentional — not a bug):** the request still succeeds and produces a draft — Gemini is explicitly instructed to use *only* the details given and never invent a name, date, or amount, so an empty `details` yields a deliberately **generic** draft (no fabricated specifics) rather than a rejected request. If you want a specific, personalized draft, supply concrete details (event name, date, amount, reason, etc.) in `details`.

**Errors:**
- `400`, missing `content_type`: `{"message": "A 'content_type' field is required."}`
- `400`, unknown `content_type`: `{"message": "Unknown content_type: '<value>'."}`  — validated *before* any Gemini call, so an invalid type never produces a `503`.
- `503`: `{"status": "ai_unavailable", "message": "...", "content_type": "<echoed>"}`

---

## 7. Redis / Caching

Caching applies **only to `/api/ai/chat`**. `/reports`, `/analytics/financial`, `/analytics/performance`, and `/content` are **never cached** — each is a fresh, one-shot Gemini call every time (they're not conversational chat turns and don't go through the Phase 6A cache layer at all).

### Cacheable vs. non-cacheable chat intents
Only intents whose answer is deterministic for a given user+message at a point in time are cached:

**Cacheable:** `Getting Started`, `Navigation`, `Membership`, `Membership Process`, `Event Registration`, `Attendance`, `Club Recommendation`, `Event Recommendation`, `Role Capabilities Q&A`, `Profile & Account`.

**Never cached:** `Financial Operations`, `Admin Questions`, `Faculty Questions`, `Application Status`, `Support Tickets`, `Rewards`, `Announcements`, `Club Creation & Governance`, `Club Discovery`, `Emergency Reporting`, `Ambiguous Request`, `Out-of-Scope` — these are either operational/frequently-changing data, or (for Emergency Reporting) never something to cache regardless of determinism.

### Cache key isolation
The cache key is derived from `user_id + role + intent + normalized_prompt` (SHA-256 hashed) — **never** the JWT itself. `normalized_prompt` is the message lowercased, trimmed, and with repeated whitespace collapsed — nothing more sophisticated (no semantic matching). This means:
- Two different users never share a cache entry, even for the identical message.
- The same user asking the identical question after a role change gets a fresh (not stale-role) answer, since role is part of the key.
- Trivial rewording of the same question (different punctuation/case/spacing aside) is treated as a *different* cache key — it is not a semantic cache.

### First-request vs. repeated-request behavior
- **First request** for a given (user, role, intent, normalized message): Redis miss → Gemini is called → on a **successful** response, the result is written to Redis (`TTL` = `AI_CACHE_TTL_SECONDS`, default 3600s / 1 hour) → response includes `"cache_hit": false`.
- **Identical repeated request** (same user, same role, same cacheable intent, same normalized message), within the TTL: served straight from Redis, Gemini is **not** called again → response includes `"cache_hit": true`, and the `response` text will be word-for-word identical to the first call.
- A **failed** Gemini call is never cached — only a successful response is ever written.
- A non-cacheable intent always shows `"cache_hit": false` (or the field may simply reflect a miss — it never becomes `true` for these intents, since they're never looked up in the cache at all).

### Conversation history
Independently of caching, the last 5 conversation exchanges (user message + assistant reply, per user) are stored in Redis and passed into every prompt automatically — this is short-term memory, not something the frontend needs to manage or resend. It expires after `AI_CACHE_HISTORY_TTL_SECONDS` (default 86400s / 24 hours).

### Redis unavailable — graceful degradation
Every cache/history function is fail-soft: if Redis can't be reached (connection refused, not running, wrong `REDIS_URL`), the module returns `None`/`[]`/no-op rather than raising. The practical effect: `/chat` keeps working exactly as if caching didn't exist — every request goes straight to Gemini, `"cache_hit"` is always `false`, and no conversation history is applied. **The rest of the platform is unaffected either way.**

### Verifying caching manually
1. Pick a cacheable intent (e.g. ask something that maps to `Membership`, like "what clubs am I a member of").
2. Send the request once — expect `"cache_hit": false`.
3. Send the **exact same** request again (same user/token, identical message text) — expect `"cache_hit": true` and identical `response` text.
4. To confirm at the Redis layer, inspect keys with `redis-cli --scan --pattern "aicache:resp:*"` (response cache) or `"aicache:history:*"` (conversation history) — do not rely on `KEYS *` in anything but a local dev instance (it blocks the server). `redis-cli monitor` can be used cautiously to watch live traffic during a manual test, but avoid leaving it running against a shared/production instance.
5. A profile edit (`PATCH /api/users/profile`) explicitly invalidates that user's entire cached AI response set (`invalidate_user_cache`), so a stale `Profile & Account` answer can't be served after a profile change — this is a scoped, per-user invalidation, never a full cache flush.

---

## 8. RBAC Quick Reference

| Role | AI capabilities | Restrictions |
|---|---|---|
| **Plain Student / Member** | All role-orthogonal chat intents; all 6 personal report types; Performance Analytics (`scope: "personal"`); all 10 content types | No `Financial Operations`, `Faculty Questions`, or `Admin Questions` chat intents; `budget`/`emergency_summary`/Financial Analytics all denied **unless** they hold a club-scoped Treasurer role, in which case `budget`/Financial Analytics are allowed scoped to that club only — `emergency_summary` stays admin-tier-only regardless |
| **Club Treasurer** (club-scoped `role_in_club`, on top of whatever platform role they have) | Everything a plain member gets, **plus**: `Financial Operations` chat intent, `budget` report, Financial Analytics — all scoped to the club(s) they treasurer | Still denied `Faculty Questions`/`Admin Questions`/`emergency_summary` unless their platform role separately grants those |
| **Other Club Officer** (President/VP/Secretary/Event or Volunteer Coordinator) | Everything a plain member gets, plus `club_activity` report and Performance Analytics `scope: "led_clubs"` for their club(s) | Not automatically granted Financial Operations/budget access — that's Treasurer-specific, not general-officer |
| **Faculty Advisor** | Everything a plain member gets, plus: `Financial Operations` and `Faculty Questions` chat intents, `budget` report, Financial Analytics, Performance Analytics `scope: "advised_clubs"` — all scoped to clubs they advise | No `Admin Questions` chat intent, no `emergency_summary` report |
| **Student Affairs Office / Dean of Student Welfare / System Admin** ("admin-tier") | Everything, platform/university-wide: `Admin Questions` chat intent, all report types including `budget` (platform-wide aggregate if they hold no club themselves) and `emergency_summary`, Financial Analytics, Performance Analytics `scope: "platform"` | None beyond the university scope itself (an admin-tier user's data is scoped to their own `university_id` where applicable) |

**Key distinctions to get right in the UI:**
- A `student` role is **not** automatically denied financial data — check the response's `authorized` field, not the user's platform role alone, since a club-scoped Treasurer role can grant it.
- `authorized: false` is a normal `200`, never a `401`/`403` — render it as an in-chat decline, not an error toast.
- `Emergency Reporting` is the one intent that is *never* gated at all, for any role.

---

## 9. Frontend Integration Notes

- **Auth/JWT:** obtain via `POST /api/auth/login`; send as `Authorization: Bearer <token>` on every AI call except `/ai/health`. Tokens are also revocable server-side (logout invalidates the specific token, not just JWT expiry) — a `401` can mean "expired," "malformed," or "revoked"; the message text differs (`"Authentication failed: <reason>"` vs. `"Token has been revoked or expired session"`) but the handling should be the same: redirect to login.
- **Request format:** JSON body on `POST /chat`, `/reports`, and `/content`. `/analytics/financial` and `/analytics/performance` don't parse a request body at all (no fields are read) — a bodyless request works fine; sending `{}` is also fine and is the safer convention to standardize on across your API client.
- **Response interpretation:** always check `status` first (`"ok"` vs `"ai_unavailable"` vs the `/reports` `"error"` case), then `authorized` (only relevant on `/chat` and `/reports`/`/analytics/financial`), then render the payload.
- **401/403 handling:** this API never returns a `403` for a role limitation — that's always a `200` with `authorized: false` (chat/reports/financial-analytics) or, for content/reports with a bad key, a `400`. Reserve your "not logged in" UI for actual `401`s.
- **Validation errors (`400`):** always a `{"message": "..."}` shape on `/chat` and `/content`; `/reports`' unknown-type `400` has a different shape (`{"status": "error", "message", "supported_report_types"}`) — handle these two `400` shapes separately if you want to surface the supported-types list.
- **Empty/no-data responses:** an empty `data`/`analytics` (e.g. `club_activity` for someone with no clubs) is a normal, non-error result — render "nothing to show" rather than treating it as a failure.
- **Generated text:** `response`/`summary`/`draft` are plain text (not markdown-structured for reports/analytics — the backend prompt explicitly asks Gemini to avoid markdown headers) — safe to render as plain paragraphs; `/chat`'s `response` may include light markdown (bullets, bold) since the model isn't told to avoid it there.
- **`cache_hit`:** only meaningful on `/chat`; purely informational (e.g. for a "cached" badge or debug panel) — do not branch UI behavior on it.
- **Role-specific UI:** hide/show the Financial Operations chat suggestion, Budget report option, and Financial Analytics tab based on the user's known club roles (treasurer) or platform role (faculty/admin-tier) — but always still handle an `authorized: false` response gracefully, since a UI-side guess about club roles could be stale.

---

## 10. Tested Examples

The following are drawn directly from the supplied testing evidence (`apitesting.txt` / `ai_api_responses.json`), reproduced here as evidence of actually-observed behavior — not fabricated.

### `/chat` — unauthorized Financial Operations (student, no treasurer role)
```json
{
  "authorized": false,
  "detected_intent": "Financial Operations",
  "response": "I can't help with that — that's outside what I have access to here. I can help you with financial status summaries for the Entrepreneurship Cell or Hackerspace, which are the clubs associated with your account, if that's useful.",
  "sql_context": { "clubs": [ /* the caller's own club budgets — present even though authorized:false, since this is SQL context for the refusal's club-name mention, not exposed financial detail */ ] },
  "status": "ok",
  "user_context": { "full_name": "User 3", "role": "student", "user_id": 3 }
}
```

### `/chat` — Financial Operations, faculty advisor (authorized, multi-club)
Authorized response included a per-club utilization breakdown across every advised club, e.g.: *"Robotics Society: 4,650 claimed of 55,499 allocated (~8% utilization)... AI-generated — verify on your dashboard."* — note the response itself appends a "verify on your dashboard" disclaimer for AI-generated financial figures.

### `/reports` — `budget`, system_admin (platform-wide aggregate)
```json
{
  "authorized": true,
  "data": {
    "budget_status_breakdown": { "approved": 11 },
    "expense_approval_breakdown": { "approved": 40, "pending": 2, "rejected": 3 },
    "total_allocated_amount": 559499.0,
    "total_expenses_claimed": 51700.0
  },
  "label": "Budget Report",
  "report_type": "budget",
  "status": "ok",
  "summary": "Budget Report\nPrepared for: User 5 (system_admin)\n\nThe total budget allocated for the platform is 559,499.00. To date, total expenses claimed amount to 51,700.00. ..."
}
```

### `/reports` — `budget`, student who is a club treasurer (scoped, not denied)
Same request (`{"report_type": "budget"}`) from a `student`-role user returned `"authorized": true` with `data.clubs` scoped to only the club(s) — e.g. "Entrepreneurship Cell" — where that student holds the `TREASURER` `role_in_club`. This is the confirmed, intentional treasurer-scoping behavior described in Section 4/8 above, not a leak.

### `/content` — `announcement` (tested)
Returned a short, non-marketing announcement draft consistent with the "plain, informative tone" instruction — response example not reproduced verbatim here to avoid restating generated content already covered by the shape example in Section 6.

*Response example for `GET /ai/health` and for the raw `/analytics/*` payload structure: not fully reproduced verbatim here beyond the shapes already shown in Sections 3/5 — the supplied evidence confirms the shape but this document intentionally shows the shape once rather than duplicating near-identical JSON per role.*
