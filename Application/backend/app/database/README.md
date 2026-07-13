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
budgets, support tickets, rewards, sponsorships). This package is the data
layer: a SQLAlchemy ORM schema of **24 tables** across 8 functional modules,
runnable locally on SQLite, with a relational design kept reasonably
portable to MySQL for a later deployment stage.

The schema reflects all 15 recommendations from the team's
*Database Design Review & Recommendations* document (merged membership
lifecycle, no calendar-sync/AI-interaction/ticket-upvote/chat tables,
embedded expense approval, minimal soft-delete, shared documents/
notifications, independent attendance, and Sponsor/ClubSponsor kept separate
because a sponsor can support multiple clubs).

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
                ├── README.md          (this file)
                ├── models/
                │   ├── __init__.py
                │   ├── auth.py
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
| `mixins.py` | `TimestampMixin`, `SoftDeleteMixin` (only used where genuinely useful — see Recommendation 9) |
| `init_db.py` | Creates the local SQLite database and all tables |
| `verify_db.py` | Checks mapper config, table count, and table-name parity |
| `seed_sample_data.py` | The one supported way to load ALL sample data: creates the 8 sample users with real Werkzeug password hashes, then runs `sql/sample_data.sql` for every other table |
| `models/__init__.py` | Imports every model so all tables register with `Base.metadata` |
| `models/auth.py` | `User`, `AuthSession` |
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
| `tests/test_auth_password_hashing.py` | Proves passwords are stored as Werkzeug hashes (never plaintext) and that `check_password_hash()` accepts correct / rejects incorrect passwords |
| `sql/sample_data.sql` | Realistic fictional data for every table except `users` (see Password Hashing section) |
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
.venv\Scripts\activate.bat
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
```

`Werkzeug` is used directly for `generate_password_hash()` /
`check_password_hash()` (see Password Hashing below). It's also a normal
Flask dependency, so if this package is merged into an existing Flask
backend, don't add it twice — merge `requirements.txt` entries carefully
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
Tables created: 24
  - announcements
  - attendance_records
  - auth_sessions
  - budgets
  - club_creation_requests
  - club_memberships
  - club_sponsors
  - clubs
  - committee_memberships
  - committees
  - documents
  - emergency_reports
  - event_registrations
  - events
  - expenses
  - external_participants
  - notifications
  - reward_points_ledger
  - reward_redemptions
  - sponsors
  - support_tickets
  - ticket_responses
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

This checks: SQLAlchemy mapper configuration, expected table count (24),
exact table names, and that the SQLite file actually contains those tables.

Tested output:

```
Mapper configuration: OK
Mapped tables in metadata: 24 (expected 24)
SQLite file: <...>\Application\backend\app\database\clubconnect.db
Tables in SQLite: 24
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
- Plaintext passwords and password hashes must never be embedded inside
  auth tokens or session identifiers. The existing `auth_sessions` table
  only stores a `jti` (token identifier) and its expiry/revocation
  status — no password material.
- This package does not introduce JWT. `auth_sessions` already existed for
  tracking issued tokens, but no token-issuing/JWT code exists yet in this
  database-only package — that's a Flask route/auth-layer concern to add
  later, not a schema change.
- Sample users are seeded with real hashes by `seed_sample_data.py` (see
  Load Sample Data), all sharing the demo password `ClubConnect#2026` for
  local testing convenience — e.g. `priya.sharma@campus.edu` /
  `ClubConnect#2026`.
- Automated proof lives in `tests/test_auth_password_hashing.py`: a stored
  hash never equals the plaintext, `check_password_hash()` returns `True`
  for the correct password and `False` for an incorrect one.

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
rows (see Password Hashing below), so its FK-dependent inserts expect users
to already exist.

Required working directory: `Application\backend\app\`

```powershell
python -m database.seed_sample_data
```

This does two things, in order:

1. Inserts the 8 sample users via SQLAlchemy, each with a real
   Werkzeug-generated `password_hash` (never plaintext).
2. Executes the rest of `sql/sample_data.sql` — `auth_sessions`, clubs,
   memberships, events, finance, support, rewards, sponsorships — covering
   every remaining table with realistic fictional data respecting every
   FK/unique/check constraint.

It's safe to re-run: if `users` already has rows, it skips user creation
instead of raising a duplicate-id error.

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
34 passed, 135 warnings in 1.37s
```

(31 original tests + 3 new password-hashing tests. The warnings are
`datetime.utcnow()` deprecation notices from the Python standard library —
harmless, not test failures.)

Categories covered: mapper configuration, table count/names, CRUD across
every major workflow (auth, memberships, events, finance, support, rewards,
sponsorships), one-to-many and many-to-many relationships, foreign-key
enforcement, unique and composite-unique constraints, check constraints,
CASCADE / SET NULL / RESTRICT delete behavior, and password hashing
(stored-as-hash, correct-password-accepted, incorrect-password-rejected).

## Run Individual Test Files

```powershell
python -m pytest database\tests\test_schema.py -v
python -m pytest database\tests\test_crud.py -v
python -m pytest database\tests\test_relationships.py -v
python -m pytest database\tests\test_constraints.py -v
python -m pytest database\tests\test_auth_password_hashing.py -v
```

## Run Raw SQL Test Queries

`sql/test_queries.sql` has 35 practical read queries (filters, joins,
aggregates) covering every table and relationship — each was individually
executed against a freshly loaded sample database with zero failures. Run
them the same way as sample data (Option A/B/C above), or copy individual
queries into VS Code's SQLite Viewer / DBeaver / DB Browser query panel.

## API-Oriented SQL Examples

`sql/api_query_examples.sql` maps realistic REST endpoints (e.g.
`GET /clubs/{id}/members`, `PATCH /expenses/{id}/approve`) to the SQL each
would run, with safe `:named` placeholders — never raw string
concatenation. These statements were syntax- and constraint-validated
against the schema. They are reference material for backend developers,
showing which tables/joins/params an endpoint needs. **The actual Flask
backend should use the SQLAlchemy ORM (`models/`), not execute these
strings directly.**

## Database Models and Modules

| Model file | Responsibility | Main entities |
|---|---|---|
| `auth.py` | Login & sessions | `User`, `AuthSession` |
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
  tracked entirely through `club_memberships`, whose `status` field carries
  the full lifecycle from application to active membership (no separate
  "applications" table — per Recommendation 1).
- Registering for an event does not imply attendance —
  `event_registrations` and `attendance_records` are separate, so a no-show
  is distinguishable from an attendee (per Recommendation 13).
- A club may organize multiple events; an event belongs to exactly one
  club.
- Expenses belong to a budget, and each expense carries its own
  one-time approval fields directly — `approval_status`, `approved_by`,
  `approval_date`, `approval_remarks` (no separate approvals table, per
  Recommendation 3).
- A sponsor may support multiple clubs, and a club may have multiple
  sponsors — `club_sponsors` is the many-to-many association table between
  them (kept separate per Recommendation 15, since sponsors are reused
  across clubs).
- `documents` and `notifications` are both shared, generic tables reused
  across modules (certificates, receipts, event reminders, ticket updates,
  etc.) rather than one table per use case (per Recommendations 11–12).
- No calendar-sync, calendar-event-mapping, AI-interaction, ticket-upvote,
  chat, or dedicated audit-log tables exist — these are intentionally
  omitted per Recommendations 2, 4, 5, 6, 7, and 10.
- Soft deletion (`deleted_at`) is limited to `User` and `Club`, where
  recoverability is genuinely useful, per Recommendation 9.
- No `public_id`/UUID columns — integer primary keys only, per
  Recommendation 8.

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

-- CommitteeMembership -> ClubMembership -> Committee: who sits on which
-- committee, resolved back to the person via their club membership
SELECT u.full_name, comm.name AS committee_name
FROM committee_memberships cmm
JOIN club_memberships cm ON cm.id = cmm.membership_id
JOIN users u ON u.id = cm.user_id
JOIN committees comm ON comm.id = cmm.committee_id;

-- Finance example: pending expenses against their club's budget
SELECT c.name AS club_name, b.period_start, ex.description, ex.amount
FROM expenses ex
JOIN budgets b ON b.id = ex.budget_id
JOIN clubs c ON c.id = b.club_id
WHERE ex.approval_status = 'pending';

-- Compare registrations vs attendance for an event
SELECT u.full_name
FROM event_registrations er JOIN users u ON u.id = er.user_id
WHERE er.event_id = 1
  AND er.user_id NOT IN (SELECT user_id FROM attendance_records WHERE event_id = er.event_id);
```

More comprehensive queries live in `sql/test_queries.sql` — this section is
intentionally short.

## Common Errors and Troubleshooting

| # | Symptom | Likely cause | Fix |
|---|---|---|---|
| 1 | `'python' is not recognized` | Python not on PATH | Try `py` instead, or reinstall Python with "Add to PATH" checked |
| 2 | `'py' is not recognized` | Python not installed / different install method | Install Python from python.org |
| 3 | `'pip' is not recognized` | pip missing from PATH | Use `python -m pip install ...` instead |
| 4 | Commands "work" but packages missing | venv not activated | Confirm `(.venv)` shows in your prompt; re-run the activation command |
| 5 | PowerShell blocks `Activate.ps1` | Script execution policy | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |
| 6 | `ModuleNotFoundError: No module named 'database'` | Wrong working directory | `cd` into `Application\backend\app\` first |
| 7 | `ModuleNotFoundError: No module named 'sqlalchemy'` | Dependencies not installed, or wrong venv active | `pip install -r Application\backend\requirements.txt` |
| 8 | `ModuleNotFoundError: No module named 'pytest'` | Same as above | Same fix — pytest is in `requirements.txt` |
| 9 | Import errors right after cloning | Fresh clone has no venv yet | Create and activate a venv, then install dependencies |
| 10 | Everything above looks right but paths still fail | Wrong capitalization: typed `application` instead of `Application` | Match the exact repo folder name — capital `A`, matters on Linux/case-sensitive systems |
| 11 | `sqlite3.OperationalError: unable to open database file` | `.db` file not created yet | Run `python -m database.init_db` first |
| 12 | `.db` file appears in an unexpected place | Command run from the wrong directory | The `.db` path is fixed relative to `database.py`'s own location — re-check you're in `Application\backend\app\` when running `init_db`/`verify_db` |
| 13 | `no such table: <name>` | Database not initialized, or stale `.db` from before a schema change | Delete `clubconnect.db`, re-run `init_db` |
| 14 | Foreign keys don't seem enforced | Direct `sqlite3` CLI session without the pragma | Our Python code enables `PRAGMA foreign_keys = ON` automatically; a raw `sqlite3` CLI session needs `PRAGMA foreign_keys = ON;` typed manually per session |
| 15 | Import errors that look circular | Model file imports another model class directly instead of by string | All cross-file relationships use string references (e.g. `relationship("ClubMembership", ...)`) — if you added a new one, follow the same pattern |
| 16 | Tests suddenly fail after a schema change | Stale local `clubconnect.db` doesn't match new models | Tests use their own in-memory DB (`conftest.py`), so this shouldn't affect tests — but delete and re-`init_db` your local dev `.db` regardless |
| 17 | Two teammates get different results locally | One has stale sample data / different `.db` state | `.db` files aren't committed to Git (see `.gitignore`) — everyone should `init_db` + load sample data fresh |
| 18 | `.venv`, `.db`, or `__pycache__` show up in `git status` | Missing/incomplete `.gitignore` | Confirm `.gitignore` includes the entries in the section below |
| 19 | VS Code/Pylance shows `Import "sqlalchemy" could not be resolved` even though tests pass at the command line | Pylance is pointed at a different Python interpreter than the one with your venv | `Ctrl+Shift+P` → **Python: Select Interpreter** → choose `Application\backend\.venv\Scripts\python.exe` |
| 20 | Duplicate sample-data / `UNIQUE constraint failed` when seeding | `seed_sample_data` (or `sample_data.sql`) already run once against this `.db` | Either re-run `seed_sample_data` (it skips user creation if users already exist) after deleting and re-initializing the `.db` for a fully clean load, or don't re-run seeding against a `.db` that already has data |

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
- `.env` files or any credentials

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
