# ClubConnect Database Package

Operational guide for the ClubConnect SQLAlchemy database package: setup,
running, testing, and troubleshooting. If you just cloned the repo, start at
Quick Start.

> **Note on the `.db` filename:** the code creates `clubconnect.db` (matching
> the `ClubConnect` project/class naming used throughout the models). If your
> team has renamed the project, only `database.py`'s `DB_PATH` needs to
> change — nothing else depends on the literal filename.

## Quick Start

Run these in order, from the directories stated. All commands below were
tested against this exact package.

```powershell
# 1. Clone (skip if already cloned)
git clone <repository-url>
cd <repository-folder>

# 2. Move into the backend folder
cd Application\backend

# 3. Create and activate a virtual environment INSIDE Application\backend\
python -m venv .venv
.venv\Scripts\Activate.ps1
```

CMD instead of PowerShell:

```bat
.venv\Scripts\activate
```

```powershell
# 4. Install dependencies
pip install -r requirements.txt

# 5. Move into the database package's parent folder
cd app

# 6. Initialize the SQLite database
python -m database.init_db

# 7. Verify it
python -m database.verify_db

# 8. Run the automated tests
python -m pytest database\tests\ -v

# 9. Load all sample data, including real password-hashed users
#    (see "Load Sample Data" below for details)
python -m database.seed_sample_data
```

**The virtual environment lives at `Application\backend\.venv\`** — not at
the repository root. Everything below assumes this location.

## ClubConnect Database Overview

ClubConnect is a student club management system (clubs, memberships, events,
budgets, support tickets, rewards, sponsorships, academics, interests, and
club-join applications). This package is the data layer: a SQLAlchemy ORM
schema of **33 tables**, runnable locally on SQLite, with a relational
design kept reasonably portable to MySQL for a later deployment stage.

The original design covered 24 tables. **9 tables were added** on top of
that baseline to support academic profiles, interest-based recommendations,
and a structured club-join workflow:

- `departments` — academic departments
- `programs` — degree programs, linked to a department
- `student_profiles` — a student's academic year/semester/batch/section
- `interests` — a shared catalog of interest tags
- `user_interests` — a user's declared interests (many-to-many)
- `club_interests` — a club's declared interests (many-to-many)
- `event_interests` — an event's topic tags (many-to-many)
- `club_join_applications` — structured join requests (motivation, resume,
  reviewer, decision) instead of going straight to `club_memberships`
- `application_interests` — interests listed on a specific join application

## Actual Folder Structure

```
<repository-root>/
└── Application/
    ├── frontend/
    └── backend/
        ├── requirements.txt
        ├── .venv/                     (created locally — not committed)
        └── app/
            └── database/
                ├── __init__.py
                ├── database.py
                ├── base.py
                ├── enums.py
                ├── mixins.py
                ├── init_db.py
                ├── verify_db.py
                ├── seed_sample_data.py
                ├── session_manager.py
                ├── db.json
                ├── README.md          (this file)
                ├── models/
                │   ├── __init__.py
                │   ├── auth.py
                │   ├── academics.py
                │   ├── interests.py
                │   ├── applications.py
                │   ├── clubs.py
                │   ├── events.py
                │   ├── finance.py
                │   ├── communication.py
                │   ├── support.py
                │   ├── rewards.py
                │   └── external_relations.py
                ├── tests/
                │   ├── __init__.py
                │   ├── conftest.py
                │   ├── test_schema.py
                │   ├── test_crud.py
                │   ├── test_relationships.py
                │   ├── test_constraints.py
                │   ├── test_new_schema.py
                │   └── test_auth_password_hashing.py
                └── sql/
                    ├── sample_data.sql
                    ├── test_queries.sql
                    └── api_query_examples.sql
```

**Note the capital `A` in `Application/`.** This matters on case-sensitive
filesystems (Linux/most deployment environments) even though Windows won't
complain locally.

## Purpose of Every File

| File | Purpose |
|---|---|
| `__init__.py` (database package) | Exposes `Base`, `engine`, `SessionLocal`, `get_session`, `init_engine` |
| `database.py` | SQLite engine/session config, FK-enforcement pragma, portable `.db` path |
| `base.py` | Shared SQLAlchemy declarative `Base` |
| `enums.py` | All enum classes (roles, statuses, etc.) used across models |
| `mixins.py` | `TimestampMixin`, `SoftDeleteMixin` |
| `init_db.py` | Creates the local SQLite database and all tables |
| `verify_db.py` | Checks mapper config, table count, and table-name parity |
| `seed_sample_data.py` | The one supported way to load ALL sample data: creates the 9 sample users with real Werkzeug password hashes, runs `sql/sample_data.sql` for every other table, then seeds 2 real login sessions via `session_manager` |
| `session_manager.py` | JWT session helpers: generate/store a login token, look it up, validate it, delete it on logout, clean up expired ones (see JWT Authentication Flow below) |
| `db.json` | Mock demo data for all 33 tables plus sample API responses, for frontend/API development — contains no real passwords, hashes, tokens, or secrets |
| `models/__init__.py` | Imports every model so all tables register with `Base.metadata` |
| `models/auth.py` | `User`, `AuthSession` |
| `models/academics.py` | `Department`, `Program`, `StudentProfile` |
| `models/interests.py` | `Interest`, `UserInterest`, `ClubInterest`, `EventInterest` |
| `models/applications.py` | `ClubJoinApplication`, `ApplicationInterest` |
| `models/clubs.py` | `Club`, `ClubCreationRequest`, `ClubMembership`, `Committee`, `CommitteeMembership`, `Announcement` |
| `models/events.py` | `Event`, `EventRegistration`, `AttendanceRecord`, `VolunteerAssignment`, `ExternalParticipant` |
| `models/finance.py` | `Budget`, `Expense` (approval embedded) |
| `models/communication.py` | `Notification`, `Document` |
| `models/support.py` | `SupportTicket`, `TicketResponse`, `EmergencyReport` |
| `models/rewards.py` | `RewardPointsLedger`, `RewardRedemption` |
| `models/external_relations.py` | `Sponsor`, `ClubSponsor` |
| `tests/conftest.py` | Pytest fixture: fresh in-memory SQLite DB per test |
| `tests/test_schema.py` | Mapper config, table count, exact table names |
| `tests/test_crud.py` | Insert/select/update/delete across all major workflows |
| `tests/test_relationships.py` | One-to-many and many-to-many navigation |
| `tests/test_constraints.py` | FK enforcement, unique/composite-unique, check constraints, CASCADE/SET NULL/RESTRICT |
| `tests/test_new_schema.py` | Academics/interests/applications schema, plus JWT session-tracking helpers |
| `tests/test_auth_password_hashing.py` | Proves passwords are stored as Werkzeug hashes (never plaintext) and that `check_password_hash()` accepts correct / rejects incorrect passwords |
| `sql/sample_data.sql` | Realistic fictional data for every table except `users` and `auth_sessions` (see Password Hashing and JWT sections below) |
| `sql/test_queries.sql` | Practical read queries covering every table/relationship |
| `sql/api_query_examples.sql` | SQL mapped to realistic REST endpoints, for backend reference |

## Prerequisites

- **Python 3.10+** — check with `python --version` or `py --version`
- **Git** — check with `git --version`
- **pip** (bundled with Python)
- VS Code recommended, with the SQLite Viewer extension (optional)

On Windows, some setups only recognize `py` instead of `python` — if a
command below fails with "not recognized", substitute `py` for `python`.

## Clone the Repository

```powershell
git clone <repository-url>
cd <repository-folder>
```

Replace `<repository-url>` and `<repository-folder>` with your team's
actual GitHub repo URL and the folder Git creates.

## Working Directory Rules

This is the most common source of local setup errors — commands must be
run from the correct folder.

| Command(s) | Required working directory |
|---|---|
| `python -m venv .venv`, activation, `pip install` | `Application\backend\` (the venv lives at `Application\backend\.venv\`) |
| `python -m database.init_db`, `python -m database.verify_db`, `python -m database.seed_sample_data` | `Application\backend\app\` |
| `pytest database\tests\ -v` | `Application\backend\app\` |
| Loading/running `.sql` files | `Application\backend\app\database\` (or reference paths relative to wherever you run it) |

Do **not** mix these — e.g. running `python -m database.init_db` from the
repository root will fail with `ModuleNotFoundError: No module named
'database'`, because there is no `database` package directly at the root.

## Create and Activate a Virtual Environment

The venv is created **inside `Application\backend\`**, not at the
repository root.

**Windows PowerShell:**

```powershell
cd Application\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

You'll know it worked when your prompt shows `(.venv)`.

## Install Dependencies

From `Application\backend\` (with the venv activated):

```powershell
pip install -r requirements.txt
```

Current dependencies:

```
SQLAlchemy>=2.0
pytest>=7.0
Werkzeug>=2.3
Flask-JWT-Extended>=4.6
```

`Werkzeug` is used directly for `generate_password_hash()` /
`check_password_hash()` (see Password Hashing below). `Flask-JWT-Extended`
is used by `session_manager.py` to generate the real JWT stored in
`auth_sessions` (see JWT Authentication Flow below). Both are also normal
Flask dependencies, so if this package is merged into an existing Flask
backend, don't add them twice — merge `requirements.txt` entries carefully
rather than overwriting teammates' file.

## Initialize the SQLite Database

Required working directory: `Application\backend\app\`

```powershell
cd Application\backend\app
python -m database.init_db
```

Tested output:

```
ClubConnect SQLite database initialized successfully.
Database file: <...>\Application\backend\app\database\clubconnect.db
Tables created: 33
  - announcements
  - application_interests
  - attendance_records
  - auth_sessions
  - budgets
  - club_creation_requests
  - club_interests
  - club_join_applications
  - club_memberships
  - club_sponsors
  - clubs
  - committee_memberships
  - committees
  - departments
  - documents
  - emergency_reports
  - event_interests
  - event_registrations
  - events
  - expenses
  - external_participants
  - interests
  - notifications
  - programs
  - reward_points_ledger
  - reward_redemptions
  - sponsors
  - student_profiles
  - support_tickets
  - ticket_responses
  - user_interests
  - users
  - volunteer_assignments
```

The `.db` file is created at `Application\backend\app\database\clubconnect.db`
— its path is derived from `database.py`'s own location, so it lands there
regardless of which folder you ran the command from (as long as the module
path itself resolves, per the Working Directory Rules above).

## Verify the Database

Required working directory: `Application\backend\app\`

```powershell
python -m database.verify_db
```

This checks: SQLAlchemy mapper configuration, expected table count (33),
exact table names, and that the SQLite file actually contains those tables.

Tested output:

```
Mapper configuration: OK
Mapped tables in metadata: 33 (expected 33)
SQLite file: <...>\Application\backend\app\database\clubconnect.db
Tables in SQLite: 33
Table name parity: OK (metadata matches SQLite exactly)
```

## Password Hashing

The `users.password_hash` column stores a real hash, never a plaintext
password and never a placeholder like `'hash1'`.

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Registration / user creation:
user.password_hash = generate_password_hash(plaintext_password)

# Login validation:
check_password_hash(user.password_hash, submitted_password)  # True/False
```

- `generate_password_hash()` salts and hashes the password (scrypt by
  default in current Werkzeug) — the same password produces a different
  hash every time, and the plaintext is never recoverable from it.
- `check_password_hash()` is the only supported way to validate a login —
  never compare `password_hash` with `==`.
- Sample users are seeded with real hashes by `seed_sample_data.py` (see
  Load Sample Data), all sharing the demo password `ClubConnect#2026` for
  local testing convenience — e.g. `priya.sharma@campus.edu` /
  `ClubConnect#2026`.
- Automated proof lives in `tests/test_auth_password_hashing.py`: a stored
  hash never equals the plaintext, `check_password_hash()` returns `True`
  for the correct password and `False` for an incorrect one.

## JWT Authentication Flow

This package uses a deliberately simple, single-token session design —
no separate access/refresh tokens, no JTI-only storage, no revocation
blocklist:

```
Login
  ↓
Verify Werkzeug password hash
  ↓
Generate one full JWT with Flask-JWT-Extended
  ↓
Store complete JWT in auth_sessions
  ↓
Return same JWT to frontend
  ↓
Frontend sends Bearer token for protected APIs
  ↓
Token expires after 1 hour
  ↓
Logout deletes token record
  ↓
Cleanup removes expired session records
```

`auth_sessions` has exactly these columns: `id`, `user_id`, `token` (the
complete JWT string, unique), `created_at`, `expires_at`.

`session_manager.py` provides everything a future Flask login/logout route
needs, so the API layer never has to re-implement token storage, expiry,
or cleanup:

```python
from database.session_manager import (
    generate_and_store_token,  # call after password verification succeeds
    get_active_token,          # look up a user's current active token
    validate_stored_token,     # check a Bearer token on protected routes
    delete_token,              # call on logout
    cleanup_expired_tokens,    # run periodically (e.g. a cron job)
)

# Login route:
token = generate_and_store_token(user.id)
return {"access_token": token}

# Logout route:
delete_token(token)
```

- The token is a real JWT produced by Flask-JWT-Extended (`create_access_token`),
  valid for exactly 1 hour.
- `JWT_SECRET_KEY` is read from the environment; a dev-only fallback secret
  is used if it's unset so tests and local runs work out of the box. **The
  real Flask app must set `JWT_SECRET_KEY` via environment/config in any
  non-dev environment** — never rely on the fallback in production.
- The database/session-management layer prepares token generation and
  storage; the actual HTTP login/logout routes belong to the Flask API
  layer, which just calls the functions above.
- Run cleanup manually any time with `python -m database.session_manager`
  (from `Application\backend\app\`).

## Inspect SQLite Manually

- **Option A — VS Code SQLite Viewer extension** (easiest, no separate
  install): open `clubconnect.db` directly in VS Code's Explorer.
- **Option B — DB Browser for SQLite or DBeaver** (GUI tools, download
  separately): open `Application\backend\app\database\clubconnect.db`.
- **Option C — `sqlite3` CLI**, if installed (not bundled with Windows by
  default — install via https://sqlite.org/download.html or use Option A/B):

  ```bash
  sqlite3 Application\backend\app\database\clubconnect.db
  .tables
  .schema users
  SELECT * FROM users;
  .quit
  ```

## Load Sample Data

There is **one documented way** to load sample data — the `seed_sample_data`
script. Don't run `sample_data.sql` on its own; it no longer contains user
rows (see Password Hashing above), so its FK-dependent inserts expect users
to already exist.

Required working directory: `Application\backend\app\`

```powershell
python -m database.seed_sample_data
```

This does three things, in order:

1. Inserts the 9 sample users via SQLAlchemy, each with a real
   Werkzeug-generated `password_hash` (never plaintext).
2. Executes the rest of `sql/sample_data.sql` — clubs, memberships, events,
   finance, support, rewards, sponsorships, academics, interests, club-join
   applications — covering every remaining table with realistic fictional
   data respecting every FK/unique/check constraint.
3. Seeds 2 real, active login sessions in `auth_sessions` by calling
   `session_manager.generate_and_store_token()` (genuine 1-hour JWTs, not
   fake placeholder values).

It's safe to re-run: if `users` (or `auth_sessions`) already has rows, it
skips that step instead of raising a duplicate-id error.

Run `init_db` first if you haven't — the tables must exist before seeding.

## Run Automated Tests

Required working directory: `Application\backend\app\`

```powershell
python -m pytest database\tests\ -v
```

Tests run against a fresh in-memory SQLite database per test (via
`tests/conftest.py`) — they never touch or depend on your local
`clubconnect.db`, so it's always safe to run them.

Actually executed result (this package, this environment):

```
51 passed, 203 warnings in 2.58s
```

(The warnings are `datetime.utcnow()` deprecation notices from the Python
standard library — harmless, not test failures.)

Categories covered: mapper configuration, table count/names, CRUD across
every major workflow (auth, memberships, events, finance, support, rewards,
sponsorships), one-to-many and many-to-many relationships, foreign-key
enforcement, unique and composite-unique constraints, check constraints,
CASCADE / SET NULL / RESTRICT delete behavior, password hashing
(stored-as-hash, correct-password-accepted, incorrect-password-rejected),
academics/interests/club-join-application schema, and the JWT session
helpers (real-token generation, active-token lookup, validation, logout
deletion, expired-session cleanup).

## Run Individual Test Files

```powershell
python -m pytest database\tests\test_schema.py -v
python -m pytest database\tests\test_crud.py -v
python -m pytest database\tests\test_relationships.py -v
python -m pytest database\tests\test_constraints.py -v
python -m pytest database\tests\test_new_schema.py -v
python -m pytest database\tests\test_auth_password_hashing.py -v
```

## Run Raw SQL Test Queries

`sql/test_queries.sql` has 46 practical read queries (filters, joins,
aggregates) covering every table and relationship — each was individually
executed against a freshly loaded sample database with zero failures. Run
them the same way as sample data (Option A/B/C above), or copy individual
queries into VS Code's SQLite Viewer / DBeaver / DB Browser query panel, or
from Python:

```python
import sqlite3
conn = sqlite3.connect("clubconnect.db")
conn.execute("PRAGMA foreign_keys = ON")
for row in conn.execute("SELECT token, created_at, expires_at FROM auth_sessions WHERE user_id = 1"):
    print(row)
```

## API-Oriented SQL Examples

`sql/api_query_examples.sql` maps realistic REST endpoints (e.g.
`GET /clubs/{id}/members`, `PATCH /expenses/{id}/approve`,
`POST /auth/logout`) to the SQL each would run, with safe `:named`
placeholders — never raw string concatenation. These statements were
syntax- and constraint-validated against the schema. They are reference
material for backend developers, showing which tables/joins/params an
endpoint needs. **The actual Flask backend should use the SQLAlchemy ORM
(`models/`) and `session_manager.py`, not execute these strings directly.**

## Database Models and Modules

| Model file | Responsibility | Main entities |
|---|---|---|
| `auth.py` | Login & sessions | `User`, `AuthSession` |
| `academics.py` | Academic structure | `Department`, `Program`, `StudentProfile` |
| `interests.py` | Interest tagging & matching | `Interest`, `UserInterest`, `ClubInterest`, `EventInterest` |
| `applications.py` | Club-join workflow | `ClubJoinApplication`, `ApplicationInterest` |
| `clubs.py` | Clubs & membership lifecycle | `Club`, `ClubCreationRequest`, `ClubMembership`, `Committee`, `CommitteeMembership`, `Announcement` |
| `events.py` | Events & participation | `Event`, `EventRegistration`, `AttendanceRecord`, `VolunteerAssignment`, `ExternalParticipant` |
| `finance.py` | Budgets & expenses | `Budget`, `Expense` |
| `communication.py` | Shared comms | `Notification`, `Document` |
| `support.py` | Helpdesk | `SupportTicket`, `TicketResponse`, `EmergencyReport` |
| `rewards.py` | Gamification | `RewardPointsLedger`, `RewardRedemption` |
| `external_relations.py` | Sponsorships | `Sponsor`, `ClubSponsor` |

All models use conventional, readable SQLAlchemy declarative syntax
(`Column`, `Integer`, `String`, `ForeignKey`, `relationship`,
`UniqueConstraint`, `CheckConstraint`) rather than the newer
`Mapped`/`mapped_column` typed style, so the schema is approachable to
teammates who know basic Python, SQL, primary/foreign keys, and
relationships without needing to learn `Mapped[...]` generics first.

## Important Relationships (Plain Language)

- A user may belong to multiple clubs; a club may have multiple members —
  tracked entirely through `club_memberships`.
- A student first submits a `club_join_applications` row (motivation,
  optional resume document, optional reviewer/decision); approval is a
  separate concern from the eventual `club_memberships` row.
- Registering for an event does not imply attendance —
  `event_registrations` and `attendance_records` are separate, so a no-show
  is distinguishable from an attendee.
- A club may organize multiple events; an event belongs to exactly one
  club.
- Expenses belong to a budget, and each expense carries its own
  one-time approval fields directly — `approval_status`, `approved_by`,
  `approval_date`, `approval_remarks`.
- A sponsor may support multiple clubs, and a club may have multiple
  sponsors — `club_sponsors` is the many-to-many association table between
  them.
- `documents` and `notifications` are both shared, generic tables reused
  across modules (certificates, receipts, event reminders, ticket updates,
  etc.) rather than one table per use case.
- `interests` is a shared catalog; `user_interests`, `club_interests`,
  `event_interests`, and `application_interests` are the many-to-many
  links used to power interest-based recommendations.
- A `student_profiles` row is one-to-one with a `User` and links to a
  `Program`, which in turn links to a `Department`.
- Soft deletion (`deleted_at`) is limited to `User` and `Club`, where
  recoverability is genuinely useful.
- No `public_id`/UUID columns — integer primary keys only.
- A user's active login session is one row in `auth_sessions` holding the
  complete JWT string — see JWT Authentication Flow above.

## Useful SQL Examples

```sql
-- List all clubs
SELECT id, name, status FROM clubs;

-- User -> ClubMembership -> Club: a member's clubs and their role in each
SELECT u.full_name, c.name AS club_name, cm.role_in_club, cm.status
FROM users u
JOIN club_memberships cm ON cm.user_id = u.id
JOIN clubs c ON c.id = cm.club_id
WHERE u.id = 1;

-- EventRegistration -> User -> Event -> AttendanceRecord: who registered
-- for an event and whether they actually checked in (no-shows have no
-- attendance_records row)
SELECT u.full_name, e.title,
       CASE WHEN ar.id IS NOT NULL THEN 'attended' ELSE 'no-show' END AS attendance
FROM event_registrations er
JOIN users u ON u.id = er.user_id
JOIN events e ON e.id = er.event_id
LEFT JOIN attendance_records ar ON ar.event_id = er.event_id AND ar.user_id = er.user_id
WHERE e.id = 1;

-- A user's declared interests
SELECT i.name FROM user_interests ui JOIN interests i ON i.id = ui.interest_id WHERE ui.user_id = 1;

-- Recommend clubs sharing at least one interest with a user
SELECT DISTINCT c.name
FROM club_interests ci JOIN clubs c ON c.id = ci.club_id
WHERE ci.interest_id IN (SELECT interest_id FROM user_interests WHERE user_id = 1);

-- A user's current login session
SELECT token, created_at, expires_at FROM auth_sessions WHERE user_id = 1;
```

More comprehensive queries live in `sql/test_queries.sql` — this section is
intentionally short.

## db.json (Frontend/API Mock Data)

`db.json` contains demo/mock data for all 33 tables plus a set of sample
API response shapes (`api_response_examples`), so frontend and API
development can proceed without a live database.

**Security note:** `db.json` must never contain real passwords, password
hashes, JWT tokens, or secrets. The `auth_sessions` entries use a clearly
labeled placeholder string instead of a real token, and `login_success` in
`api_response_examples` uses a `<full_jwt_token>` placeholder rather than
an actual JWT. If you regenerate this file, keep it that way.

## Common Errors and Troubleshooting

| # | Symptom | Likely cause | Fix |
|---|---|---|---|
| 1 | `'python' is not recognized` | Python not on PATH | Try `py` instead, or reinstall Python with "Add to PATH" checked |
| 2 | `'py' is not recognized` | Python not installed / different install method | Install Python from python.org |
| 3 | `'pip' is not recognized` | pip missing from PATH | Use `python -m pip install ...` instead |
| 4 | Commands "work" but packages missing | venv not activated | Confirm `(.venv)` shows in your prompt; re-run the activation command |
| 5 | PowerShell blocks `Activate.ps1` | Script execution policy | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |
| 6 | `ModuleNotFoundError: No module named 'database'` | Wrong working directory | `cd` into `Application\backend\app\` first |
| 7 | `ModuleNotFoundError: No module named 'sqlalchemy'` (or `flask_jwt_extended`, `werkzeug`) | Dependencies not installed, or wrong venv active | `pip install -r Application\backend\requirements.txt` from an activated venv |
| 8 | `ModuleNotFoundError: No module named 'pytest'` | Same as above | Same fix — pytest is in `requirements.txt` |
| 9 | Import errors right after cloning | Fresh clone has no venv yet | Create and activate a venv, then install dependencies |
| 10 | Everything above looks right but paths still fail | Wrong capitalization: typed `application` instead of `Application` | Match the exact repo folder name — capital `A`, matters on Linux/case-sensitive systems |
| 11 | `sqlite3.OperationalError: unable to open database file` | `.db` file not created yet | Run `python -m database.init_db` first |
| 12 | `.db` file appears in an unexpected place | Command run from the wrong directory | The `.db` path is fixed relative to `database.py`'s own location — re-check you're in `Application\backend\app\` when running `init_db`/`verify_db` |
| 13 | `no such table: <name>` | Database not initialized, or stale `.db` from before a schema change | Delete `clubconnect.db`, re-run `init_db` |
| 14 | Foreign keys don't seem enforced | Direct `sqlite3` CLI session without the pragma | Our Python code enables `PRAGMA foreign_keys = ON` automatically; a raw `sqlite3` CLI session needs `PRAGMA foreign_keys = ON;` typed manually per session |
| 15 | `no such column: jti` (or `token_type`, `revoked_at`) in old queries/tests | Referencing the old JTI-based session design | `auth_sessions` now only has `id`, `user_id`, `token`, `created_at`, `expires_at` — update the query to use `token`/`expires_at` |
| 16 | Tests suddenly fail after a schema change | Stale local `clubconnect.db` doesn't match new models | Tests use their own in-memory DB (`conftest.py`), so this shouldn't affect tests — but delete and re-`init_db` your local dev `.db` regardless |
| 17 | Two teammates get different results locally | One has stale sample data / different `.db` state | `.db` files aren't committed to Git (see `.gitignore`) — everyone should `init_db` + load sample data fresh |
| 18 | `.venv`, `.db`, or `__pycache__` show up in `git status` | Missing/incomplete `.gitignore` | Confirm `.gitignore` includes the entries in the section below |
| 19 | VS Code/Pylance shows `Import "sqlalchemy" could not be resolved` even though tests pass at the command line | Pylance is pointed at a different Python interpreter than the one with your venv | `Ctrl+Shift+P` → **Python: Select Interpreter** → choose `Application\backend\.venv\Scripts\python.exe` |
| 20 | Duplicate sample-data / `UNIQUE constraint failed` when seeding | `seed_sample_data` (or `sample_data.sql`) already run once against this `.db` | Delete and re-`init_db` the `.db` for a fully clean load, or don't re-run seeding against a `.db` that already has data (`seed_sample_data` skips users/sessions that already exist, but re-running raw `sample_data.sql` directly can still collide) |

## Reset or Recreate the Local Database

**Safe for local development only — never run this against
shared/production data:**

1. Stop any process currently using `clubconnect.db` (close DB browser
   tools, stop the Flask server if running).
2. Confirm you're deleting the local dev file, not a shared one.
3. Delete it:

   ```powershell
   cd Application\backend\app\database
   del clubconnect.db
   ```

4. Re-initialize: `cd .. && python -m database.init_db`
5. Reload sample data if needed: `python -m database.seed_sample_data`
6. Verify: `python -m database.verify_db`
7. Run tests: `python -m pytest database\tests\ -v`

## Git and GitHub Collaboration

```bash
git checkout main
git pull origin main
git checkout -b feature/database-update

# ... make and test your changes ...

git status
git add <relevant-files>
git commit -m "Update ClubConnect database schema and tests"
git push -u origin feature/database-update
```

Then open a pull request against `main` and request a review.

**Do not commit:**

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- local `.db` files (unless your team explicitly decides to commit a shared
  dev snapshot)
- `.env` files or any credentials, including `JWT_SECRET_KEY`

### Recommended `.gitignore` entries

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.db
.env
```

## Future MySQL Migration

Current local development uses SQLite for simplicity. The relational design
(explicit FKs, constraints, no SQLite-only tricks) is intended to stay
reasonably portable, but note:

- MySQL requires an appropriate driver (e.g. PyMySQL or mysqlclient).
- The `DATABASE_URL` in `database.py` will need to change to a MySQL
  connection string.
- Some raw SQL in `sql/*.sql` may need adjustment — `CURRENT_TIMESTAMP` and
  standard JOIN/WHERE syntax used here are portable, but any future
  SQLite-specific additions should be clearly marked.
- Changing the connection URL alone does not guarantee a working
  migration — test thoroughly against MySQL before relying on it. SQLite
  and MySQL are not identical in behavior (e.g. type affinity, enum
  enforcement, and some constraint semantics differ).
