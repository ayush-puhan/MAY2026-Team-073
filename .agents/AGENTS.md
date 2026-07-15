# API Architecture Rules

All CRUD operations and API modules MUST strictly follow the dual-implementation Strategy Pattern to ensure seamless switching between a mock JSON Server and a real Flask Backend.

1. **Routing Layer**: For any new API feature (e.g., `clubs.api.js`), the root file must only serve to check `VITE_USE_MOCK_BACKEND` and export the correct implementation.
2. **Backend APIs (`src/api/backend_apis/`) [THE CONTRACT]**: Implementations here MUST perfectly map to the expected SQL/Flask structure and serve as the strict contract for the backend team.
   - Use standard REST methods (`GET`, `POST`, `PATCH`, `DELETE`).
   - Assume the backend handles complex SQL JOINs, nested inserts, and database constraints internally. The frontend must send unified JSON payloads (e.g., a single `PATCH` with nested `student_profile` dict and `interests` array) rather than making multiple HTTP requests to different tables.
   - When the `VITE_USE_MOCK_BACKEND` variable is flipped to `false`, the frontend must function perfectly without any code changes.
3. **Mock Backend APIs (`src/api/mockbackendApis/`)**: Implementations here must simulate the real backend behavior by combining multiple requests to the flat `db.json` structure provided by JSON Server to mimic the unified behavior of the real API.
4. **Never Modify Frontend State based on Mocks**: The frontend components must NEVER contain `if (USE_MOCK)`. All abstraction happens purely at the API layer.
5. **Strict Parity**: You MUST create both real and mock versions for any requested API function. If you make a bug fix or modification to one, you must evaluate and update the other to keep them perfectly in sync.
6. **Naming Conventions**: React component files (`.jsx`) and their folders must strictly use **PascalCase**. API files, utilities, and their nested folders (e.g., `backendApis/authApis/`) must use **camelCase**.

# Frontend Development Guidelines

1. **Folder Structure & File Conventions**: 
   - Group related files by feature/domain (e.g., `auth`, `dashboard`, `landing`).
   - Each component must have its own dedicated folder matching the component's **PascalCase** name (e.g., `components/ui/Button/Button.jsx`).
   - Inside the component folder, place its associated CSS module (e.g., `Button.module.css`).
2. **Component Breakdown Approach**: 
   - Avoid massive monolithic files. Break down complex user interfaces into smaller, modular, and reusable sub-components.
   - Keep files focused on a single responsibility. If a component exceeds 250-300 lines, extract its sections (e.g., headers, specific tabs, forms) into separate child components.
3. **Scoped Responsive Design (CSS Modules)**: 
   - Use CSS Modules for all styling.
   - Media queries must be nested inside the specific component container's class to keep styles locally scoped and prevent global CSS bleed. 
   - *Example*: `.container { ... @media (max-width: 768px) { ... } }`

# Database Schema & Mock Parity Rules

## General Rules

1. **Strict Integer Types**: All Foreign Keys (e.g., `program_id`, `department_id`), metadata fields (`academic_year`, `semester`), and booleans (`color_blind_mode`, `is_active`) MUST be parsed and saved strictly as integers (`parseInt()` or `1`/`0`) in API payloads. The backend strictly enforces this.
2. **Enum Handling**: Enum strings from the database (e.g., `role: "STUDENT"`, `status: "approved"`) may vary in casing. Always apply `.toLowerCase()` when doing conditional logic on the frontend (e.g., routing based on role).
3. **Many-to-Many Relationships**: Complex fields like `interests` are managed via join tables (`user_interests`, `club_interests`, `event_interests`, `application_interests`) linking to a central `interests` catalog. The frontend mock API MUST simulate this relational mapping accurately and not just store raw arrays on the parent object.
4. **Separate Approvals & Registrations**: A `club_join_application` is distinct from a `club_membership`. Likewise, an `event_registration` is distinct from an `attendance_record`. The frontend UI and mock APIs must respect these distinct states and not merge them.
5. **Mock `password` vs Real `password_hash`**: In `db.json`, the `users` table stores a plaintext `password` field for mock login convenience. The real backend stores `password_hash` (Werkzeug scrypt). The mock API uses direct string comparison; the real API sends credentials to `/auth/login` which does hash verification server-side.
6. **`student_profiles` has no `id` column**: Its primary key is `user_id` (1:1 with `users`). When querying JSON Server, use `?user_id=X` not `?id=X`.
7. **Soft Deletion**: Only `users` and `clubs` support soft delete (`deleted_at` column). All other tables use hard deletes with CASCADE.

## Enum Values Reference

| Enum | Stored Values (lowercase strings in DB) |
|---|---|
| **UserRole** | `student`, `faculty_advisor`, `student_affairs_office`, `dean_student_welfare`, `system_admin` |
| **ClubMemberRole** | `applicant`, `member`, `committee_member`, `volunteer_coordinator`, `event_coordinator`, `secretary`, `treasurer`, `vice_president`, `president` |
| **MembershipStatus** | `pending`, `approved`, `rejected`, `withdrawn` |
| **ClubStatus** | `pending`, `active`, `suspended`, `archived` |
| **ClubRequestStatus** | `submitted`, `under_review`, `approved`, `rejected` |
| **EventStatus** | `scheduled`, `ongoing`, `completed`, `cancelled` |
| **RegistrationStatus** | `registered`, `waitlisted`, `cancelled` |
| **VolunteerTaskStatus** | `assigned`, `in_progress`, `completed`, `missed` |
| **ExternalParticipantType** | `other_university_student`, `guest_speaker`, `competition_participant` |
| **BudgetStatus** | `draft`, `submitted`, `approved`, `rejected`, `closed` |
| **ExpenseStatus** | `pending`, `approved`, `rejected`, `reimbursed` |
| **ExpenseApprovalStatus** | `pending`, `approved`, `rejected` |
| **DocumentType** | `certificate`, `receipt`, `report`, `general` |
| **NotificationType** | `membership_update`, `event_reminder`, `budget_approval`, `ticket_update`, `password_reset`, `certificate_ready`, `emergency_alert`, `announcement` |
| **NotificationChannel** | `in_app`, `email`, `both` |
| **AnnouncementAudience** | `all_members`, `committee`, `leadership`, `all_students` |
| **EmergencyCategory** | `harassment`, `medical`, `wheelchair_assistance`, `other_emergency` |
| **EmergencyStatus** | `reported`, `acknowledged`, `in_progress`, `resolved` |
| **RedemptionStatus** | `requested`, `approved`, `fulfilled`, `rejected` |
| **AuthProvider** | `local`, `google` |
| **Gender** | `male`, `female`, `other`, `prefer_not_to_say` |
| **TokenType** | `access`, `refresh` |

## Complete 36-Table Schema

### TENANT MODULE (`models/university.py`)

#### `universities` (TimestampMixin, SoftDeleteMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `name` | String(200) | unique, NOT NULL |
| `short_name` | String(50) | nullable |
| `logo_url` | Text | nullable |
| `domain` | String(100) | unique, NOT NULL |
| `allowed_domains` | Text | nullable |
| `address` | Text | nullable |
| `website` | String(500) | nullable |
| `is_active` | Integer(boolean) | default=1, NOT NULL, CHECK IN (0,1) |
| `created_at` | DateTime | default=utcnow, NOT NULL |
| `updated_at` | DateTime | on update, nullable |
| `deleted_at` | DateTime | nullable (soft delete) |

**Key Relationships**: → allowed_domains (1:N), → users (1:N), → departments (1:N), → clubs (1:N), → support_tickets (1:N)

#### `university_domains`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `university_id` | Integer | FK→universities.id (CASCADE), NOT NULL |
| `domain` | String(100) | NOT NULL |

**Key Relationships**: → university (N:1)

### AUTH MODULE (`models/auth.py`)

#### `users` (TimestampMixin, SoftDeleteMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `email` | String(255) | unique, NOT NULL |
| `password_hash` | String(512) | nullable *(db.json: `password` plaintext)* |
| `full_name` | String(200) | NOT NULL |
| `roll_number` | String(50) | unique, nullable |
| `role` | String(50) | NOT NULL, CHECK IN UserRole |
| `phone` | String(20) | nullable |
| `profile_photo_url` | String(500) | nullable |
| `accessibility_prefs` | Text | nullable (JSON string) |
| `is_active` | Integer(boolean) | default=1, NOT NULL, CHECK IN (0,1) |
| `email_verified` | Integer(boolean) | default=0, NOT NULL, CHECK IN (0,1) |
| `google_id` | String(255) | unique, nullable |
| `dob` | String(20)/Date | nullable |
| `auth_provider` | String(20) | default="LOCAL", NOT NULL, CHECK IN AuthProvider |
| `department_id` | Integer | FK→departments.id (SET NULL), nullable |
| `university_id` | Integer | FK→universities.id (SET NULL), nullable *(null = global admin)* |
| `gender` | String(30) | nullable, CHECK IN Gender |
| `color_blind_mode` | Integer(boolean) | default=0, NOT NULL, CHECK IN (0,1) |
| `created_at` | DateTime | default=utcnow, NOT NULL |
| `updated_at` | DateTime | on update, nullable |
| `deleted_at` | DateTime | nullable (soft delete) |

**Key Relationships**: → student_profile (1:1), → memberships (1:N), → sessions (1:N), → user_interests (1:N via join), → club_join_applications (1:N), → department (N:1), → university (N:1)

#### `auth_sessions` (TimestampMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `token` | Text | unique, NOT NULL |
| `created_at` | DateTime | default=utcnow, NOT NULL |
| `updated_at` | DateTime | on update, nullable |
| `expires_at` | DateTime | NOT NULL |

---

### ACADEMICS MODULE (`models/academics.py`)

#### `departments`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `name` | String(200) | unique, NOT NULL |
| `code` | String(20) | unique, NOT NULL |
| `university_id` | Integer | FK→universities.id (CASCADE), NOT NULL |
| `created_at` | DateTime | NOT NULL |

**Relationships**: → programs (1:N), → users (1:N), → university (N:1)

#### `programs`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `department_id` | Integer | FK→departments.id (CASCADE), NOT NULL |
| `name` | String(200) | NOT NULL |
| `created_at` | DateTime | NOT NULL |

**Unique**: (department_id, name). **Relationships**: → department (N:1), → student_profiles (1:N)

#### `student_profiles` *(PK = user_id, NOT id)*
| Column | Type | Constraints |
|---|---|---|
| `user_id` | Integer | **PK**, FK→users.id (CASCADE) |
| `program_id` | Integer | FK→programs.id (RESTRICT), NOT NULL |
| `academic_year` | Integer | NOT NULL, CHECK 1–6 |
| `semester` | Integer | NOT NULL, CHECK 1–12 |
| `batch` | String(20) | NOT NULL |
| `section` | String(10) | nullable |
| `institutional_email` | String(255) | unique, nullable |
| `is_verified` | Integer(boolean) | default=0, NOT NULL, CHECK IN (0,1) |
| `created_at` | DateTime | NOT NULL |

**Relationships**: → user (1:1), → program (N:1). Program → Department gives the student's department.

---

### INTERESTS MODULE (`models/interests.py`)

#### `interests`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `name` | String(100) | unique, NOT NULL |
| `created_at` | DateTime | NOT NULL |

Central catalog. Linked to users, clubs, events, and applications via join tables.

#### `user_interests` (Join: users ↔ interests)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `interest_id` | Integer | FK→interests.id (CASCADE), NOT NULL |
| `created_at` | DateTime | NOT NULL |

**Unique**: (user_id, interest_id)

#### `club_interests` (Join: clubs ↔ interests)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `interest_id` | Integer | FK→interests.id (CASCADE), NOT NULL |
| `created_at` | DateTime | NOT NULL |

**Unique**: (club_id, interest_id)

#### `event_interests` (Join: events ↔ interests)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `event_id` | Integer | FK→events.id (CASCADE), NOT NULL |
| `interest_id` | Integer | FK→interests.id (CASCADE), NOT NULL |
| `created_at` | DateTime | NOT NULL |

**Unique**: (event_id, interest_id)

---

### APPLICATIONS MODULE (`models/applications.py`)

#### `club_join_applications`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `motivation` | Text | nullable |
| `contribution` | Text | nullable |
| `previous_experience` | Text | nullable |
| `skills` | Text | nullable |
| `portfolio_url` | String(500) | nullable |
| `resume_document_id` | Integer | FK→documents.id (SET NULL), nullable |
| `weekly_availability` | String(100) | nullable |
| `status` | String(20) | default="pending", CHECK IN MembershipStatus |
| `reviewed_by` | Integer | FK→users.id (SET NULL), nullable |
| `review_comments` | Text | nullable |
| `applied_at` | DateTime | default=utcnow, NOT NULL |
| `reviewed_at` | DateTime | nullable |

**Relationships**: → user (N:1), → club (N:1), → reviewer (N:1), → resume_document (N:1), → application_interests (1:N via join)

#### `application_interests` (Join: club_join_applications ↔ interests)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `application_id` | Integer | FK→club_join_applications.id (CASCADE), NOT NULL |
| `interest_id` | Integer | FK→interests.id (CASCADE), NOT NULL |

**Unique**: (application_id, interest_id)

---

### CLUBS MODULE (`models/clubs.py`)

#### `clubs` (TimestampMixin, SoftDeleteMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `name` | String(200) | unique, NOT NULL |
| `slug` | String(200) | unique, NOT NULL |
| `category` | String(100) | nullable |
| `description` | Text | nullable |
| `objectives` | Text | nullable |
| `logo_url` | String(500) | nullable |
| `status` | String(20) | default="pending", CHECK IN ClubStatus |
| `faculty_advisor_id` | Integer | FK→users.id (SET NULL), nullable |
| `member_count_cache` | Integer | default=0 |
| `university_id` | Integer | FK→universities.id (CASCADE), NOT NULL |
| `created_at` | DateTime | NOT NULL |
| `updated_at` | DateTime | nullable |
| `deleted_at` | DateTime | nullable (soft delete) |

**Relationships**: → memberships (1:N), → events (1:N), → budgets (1:N), → committees (1:N), → announcements (1:N), → club_interests (1:N), → join_applications (1:N), → club_sponsors (1:N)

#### `club_creation_requests`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `proposed_name` | String(200) | NOT NULL |
| `proposed_category` | String(100) | nullable |
| `proposal_description` | Text | nullable |
| `requested_by` | Integer | FK→users.id (CASCADE), NOT NULL |
| `status` | String(20) | default="submitted", CHECK IN ClubRequestStatus |
| `reviewed_by` | Integer | FK→users.id (SET NULL), nullable |
| `review_comments` | Text | nullable |
| `resulting_club_id` | Integer | FK→clubs.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |
| `decided_at` | DateTime | nullable |

#### `club_memberships`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `role_in_club` | String(30) | default="member", CHECK IN ClubMemberRole |
| `status` | String(20) | default="pending", CHECK IN MembershipStatus |
| `applied_at` | DateTime | default=utcnow, NOT NULL |
| `decided_at` | DateTime | nullable |
| `approved_by` | Integer | FK→users.id (SET NULL), nullable |
| `rejection_reason` | Text | nullable |

**Unique**: (user_id, club_id). **Relationships**: → user, → club, → committee_memberships (1:N), → volunteer_assignments (1:N)

#### `committees`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `name` | String(200) | NOT NULL |
| `description` | Text | nullable |
| `created_at` | DateTime | NOT NULL |

**Unique**: (club_id, name)

#### `committee_memberships`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `committee_id` | Integer | FK→committees.id (CASCADE), NOT NULL |
| `membership_id` | Integer | FK→club_memberships.id (CASCADE), NOT NULL |
| `joined_at` | DateTime | NOT NULL |

**Unique**: (committee_id, membership_id). Links club members to committees via their club_membership record.

#### `announcements`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), nullable *(null = campus-wide)* |
| `posted_by` | Integer | FK→users.id (CASCADE), NOT NULL |
| `title` | String(300) | NOT NULL |
| `body` | Text | nullable |
| `target_audience` | String(30) | default="all_members", CHECK IN AnnouncementAudience |
| `created_at` | DateTime | NOT NULL |

---

### EVENTS MODULE (`models/events.py`)

#### `events` (TimestampMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `title` | String(300) | NOT NULL |
| `description` | Text | nullable |
| `venue` | String(300) | nullable |
| `start_at` | DateTime | NOT NULL |
| `end_at` | DateTime | nullable, CHECK end_at >= start_at |
| `registration_deadline` | DateTime | nullable |
| `capacity` | Integer | nullable |
| `status` | String(20) | default="draft", CHECK IN EventStatus |
| `created_by` | Integer | FK→users.id (SET NULL), nullable |
| `requires_external_participants` | Integer(boolean) | default=0 |
| `is_public` | Integer(boolean) | default=0 |
| `created_at` | DateTime | NOT NULL |
| `updated_at` | DateTime | nullable |

**Relationships**: → club (N:1), → registrations (1:N), → attendance_records (1:N), → volunteers (1:N), → external_participants (1:N), → event_interests (1:N)

#### `event_registrations`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `event_id` | Integer | FK→events.id (CASCADE), NOT NULL |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `registered_at` | DateTime | NOT NULL |
| `status` | String(20) | default="registered", CHECK IN RegistrationStatus |
| `qr_code_token` | String(255) | unique, nullable |

**Unique**: (event_id, user_id). Registration ≠ attendance. A no-show has a registration but no attendance_record.

#### `attendance_records`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `event_id` | Integer | FK→events.id (CASCADE), NOT NULL |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `checked_in_at` | DateTime | NOT NULL |
| `recorded_by` | Integer | FK→users.id (SET NULL), nullable |

**Unique**: (event_id, user_id)

#### `volunteer_assignments`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `event_id` | Integer | FK→events.id (CASCADE), NOT NULL |
| `assignee_membership_id` | Integer | FK→club_memberships.id (CASCADE), NOT NULL |
| `assigned_by` | Integer | FK→users.id (SET NULL), nullable |
| `task_description` | Text | nullable |
| `status` | String(20) | default="assigned", CHECK IN VolunteerTaskStatus |
| `due_at` | DateTime | nullable |
| `created_at` | DateTime | NOT NULL |

Volunteers are assigned via their `club_membership`, not directly by `user_id`.

#### `external_participants`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `event_id` | Integer | FK→events.id (CASCADE), NOT NULL |
| `user_id` | Integer | FK→users.id (SET NULL), nullable *(for cross-university platform users)* |
| `full_name` | String(200) | NOT NULL |
| `email` | String(255) | nullable |
| `affiliation` | String(300) | nullable |
| `participant_type` | String(30) | nullable, CHECK IN ExternalParticipantType |
| `registered_at` | DateTime | NOT NULL |

---

### FINANCE MODULE (`models/finance.py`)

#### `budgets`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `title` | String(300) | NOT NULL |
| `period_start` | DateTime | nullable |
| `period_end` | DateTime | nullable, CHECK period_end >= period_start |
| `allocated_amount` | Integer | default=0, CHECK >= 0 |
| `status` | String(20) | default="draft", CHECK IN BudgetStatus |
| `created_by` | Integer | FK→users.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |

**Relationships**: → club (N:1), → expenses (1:N)

#### `expenses`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `budget_id` | Integer | FK→budgets.id (CASCADE), NOT NULL |
| `description` | Text | nullable |
| `amount` | Integer | NOT NULL, CHECK > 0 |
| `category` | String(100) | nullable |
| `receipt_document_id` | Integer | FK→documents.id (SET NULL), nullable |
| `submitted_by` | Integer | FK→users.id (SET NULL), nullable |
| `status` | String(20) | default="pending" |
| `approval_status` | String(20) | default="pending", CHECK IN ExpenseStatus |
| `approved_by` | Integer | FK→users.id (SET NULL), nullable |
| `approval_date` | DateTime | nullable |
| `approval_remarks` | Text | nullable |
| `created_at` | DateTime | NOT NULL |

Each expense carries its own inline approval fields — no separate approval table.

---

### COMMUNICATION MODULE (`models/communication.py`)

#### `notifications`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `type` | String(50) | NOT NULL |
| `title` | String(300) | NOT NULL |
| `body` | Text | nullable |
| `channel` | String(20) | default="in_app", CHECK IN NotificationChannel |
| `is_read` | Integer(boolean) | default=0, CHECK IN (0,1) |
| `sent_via_resend` | Integer(boolean) | default=0, CHECK IN (0,1) |
| `related_entity_type` | String(50) | nullable *(e.g., "club_membership", "event")* |
| `related_entity_id` | Integer | nullable |
| `created_at` | DateTime | NOT NULL |

Generic polymorphic notification. `related_entity_type` + `related_entity_id` form a virtual FK.

#### `documents`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `owner_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `club_id` | Integer | FK→clubs.id (SET NULL), nullable |
| `event_id` | Integer | FK→events.id (SET NULL), nullable |
| `doc_type` | String(30) | default="general", CHECK IN DocumentType |
| `file_url` | String(500) | NOT NULL |
| `title` | String(300) | nullable |
| `created_at` | DateTime | NOT NULL |

Shared across modules. Referenced by `expenses.receipt_document_id` and `club_join_applications.resume_document_id`.

---

### SUPPORT MODULE (`models/support.py`)

#### `support_tickets` (TimestampMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `raised_by` | Integer | FK→users.id (CASCADE), NOT NULL |
| `club_id` | Integer | FK→clubs.id (SET NULL), nullable |
| `title` | String(300) | NOT NULL |
| `description` | Text | nullable |
| `assigned_agent_id` | Integer | FK→users.id (SET NULL), nullable |
| `is_open` | Integer(boolean) | default=1, CHECK IN (0,1) |
| `is_offensive` | Integer(boolean) | default=0, CHECK IN (0,1) |
| `resolution_rating` | Integer | nullable, CHECK 1–5 OR NULL |
| `university_id` | Integer | FK→universities.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |
| `updated_at` | DateTime | nullable |

**Relationships**: → responses (1:N)

#### `ticket_responses`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `ticket_id` | Integer | FK→support_tickets.id (CASCADE), NOT NULL |
| `responder_id` | Integer | FK→users.id (SET NULL), nullable |
| `body` | Text | NOT NULL |
| `is_resolution` | Integer(boolean) | default=0, CHECK IN (0,1) |
| `created_at` | DateTime | NOT NULL |

#### `emergency_reports`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `reported_by` | Integer | FK→users.id (SET NULL), nullable *(anonymous allowed)* |
| `event_id` | Integer | FK→events.id (SET NULL), nullable |
| `category` | String(30) | NOT NULL, CHECK IN EmergencyCategory |
| `description` | Text | nullable |
| `status` | String(20) | default="reported", CHECK IN EmergencyStatus |
| `handled_by` | Integer | FK→users.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |
| `resolved_at` | DateTime | nullable |

---

### REWARDS MODULE (`models/rewards.py`)

#### `reward_points_ledger`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `points` | Integer | NOT NULL *(can be negative for redemptions)* |
| `reason` | String(300) | nullable |
| `source_event_id` | Integer | FK→events.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |

A user's total points = SUM(points) from all their ledger rows.

#### `reward_redemptions`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK→users.id (CASCADE), NOT NULL |
| `points_spent` | Integer | NOT NULL |
| `reward_description` | String(300) | nullable |
| `status` | String(20) | default="requested", CHECK IN RedemptionStatus |
| `approved_by` | Integer | FK→users.id (SET NULL), nullable |
| `created_at` | DateTime | NOT NULL |

---

### EXTERNAL RELATIONS MODULE (`models/external_relations.py`)

#### `sponsors`
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `organization_name` | String(300) | unique, NOT NULL |
| `contact_email` | String(255) | nullable |
| `contact_person` | String(200) | nullable |
| `created_at` | DateTime | NOT NULL |

#### `club_sponsors` (Join: clubs ↔ sponsors)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK |
| `club_id` | Integer | FK→clubs.id (CASCADE), NOT NULL |
| `sponsor_id` | Integer | FK→sponsors.id (CASCADE), NOT NULL |
| `sponsorship_details` | Text | nullable |

**Unique**: (club_id, sponsor_id)

---

### AUDIT MODULE (`models/audit.py`)

#### `audit_logs` (TimestampMixin)
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `user_id` | Integer | FK→users.id (SET NULL), nullable |
| `university_id` | Integer | FK→universities.id (CASCADE), NOT NULL |
| `action` | String(100) | NOT NULL |
| `entity_type` | String(100) | nullable |
| `entity_id` | Integer | nullable |
| `details` | Text | nullable |
| `created_at` | DateTime | default=utcnow, NOT NULL |
| `updated_at` | DateTime | on update, nullable |

**Relationships**: → user (N:1)

---

## Key Relationship Chains (for Mock API JOINs)

1. **User → Department**: `users.department_id` → `departments.id`
2. **User → Program → Department**: `student_profiles.user_id` → `users.id`, `student_profiles.program_id` → `programs.id` → `programs.department_id` → `departments.id`
3. **User → Interests**: `user_interests.user_id` → `users.id`, `user_interests.interest_id` → `interests.id`
4. **Club → Interests**: `club_interests.club_id` → `clubs.id`, `club_interests.interest_id` → `interests.id`
5. **Event → Interests**: `event_interests.event_id` → `events.id`, `event_interests.interest_id` → `interests.id`
6. **User → Club Memberships → Club**: `club_memberships.user_id` + `club_memberships.club_id`
7. **User → Club Join Applications → Club**: `club_join_applications.user_id` + `club_join_applications.club_id`
8. **Event → Club**: `events.club_id` → `clubs.id`
9. **Budget → Club**: `budgets.club_id` → `clubs.id`, **Expense → Budget**: `expenses.budget_id` → `budgets.id`
10. **Volunteer → Membership → User**: `volunteer_assignments.assignee_membership_id` → `club_memberships.id` → `club_memberships.user_id` → `users.id`
11. **Recommendation Engine**: Match `user_interests.interest_id` against `club_interests.interest_id` and `event_interests.interest_id` to suggest clubs/events.
