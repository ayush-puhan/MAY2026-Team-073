# ClubConnect Database Package

## Setup (Windows PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r application\backend\requirements.txt
```

## Initialize the SQLite database

From the repository root:

```powershell
python -m application.backend.database.init_db
```

This creates `application/backend/database/clubconnect.db` and prints the 24 tables created.

## Verify the database

```powershell
python -m application.backend.database.verify_db
```

Checks mapper configuration, mapped table count/names, and SQLite table parity.

## Where the database file lives

`application/backend/database/clubconnect.db` — the path is derived from `database.py`'s
location, so it works the same regardless of your terminal's current directory.

## What to commit to GitHub

- Commit: all `.py` files, `requirements.txt`, this `README.md`.
- Do NOT commit: `clubconnect.db` (add to `.gitignore`) or `venv/`.

## Package layout

```
application/backend/database/
├── database.py       # engine, session factory, FK pragma, init_engine()
├── base.py            # shared Declarative Base
├── enums.py            # all enum classes
├── mixins.py            # TimestampMixin, SoftDeleteMixin
├── init_db.py            # creates the local SQLite database
├── verify_db.py            # validates schema + SQLite parity
└── models/
    ├── auth.py               # User, AuthSession
    ├── clubs.py                # Club, ClubCreationRequest, ClubMembership, Committee, CommitteeMembership, Announcement
    ├── events.py                 # Event, EventRegistration, AttendanceRecord, VolunteerAssignment, ExternalParticipant
    ├── finance.py                  # Budget, Expense
    ├── communication.py              # Notification, Document
    ├── support.py                      # SupportTicket, TicketResponse, EmergencyReport
    ├── rewards.py                        # RewardPointsLedger, RewardRedemption
    └── external_relations.py               # Sponsor, ClubSponsor
```
