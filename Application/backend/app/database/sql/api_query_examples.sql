-- ClubConnect API-oriented SQL reference examples.
--
-- These map realistic backend REST endpoints to the SQL each would run.
-- They use safe :named placeholders -- never raw string concatenation.
--
-- IMPORTANT: this file is REFERENCE MATERIAL for backend developers showing
-- which tables/joins/params an endpoint needs. The actual Flask backend
-- should use the SQLAlchemy ORM (see ../models/), not execute these raw
-- strings directly.

-- GET /clubs
SELECT id, name, slug, category, status FROM clubs WHERE status = 'active';

-- GET /clubs/{club_id}
SELECT id, name, slug, category, description, status, faculty_advisor_id
FROM clubs WHERE id = :club_id;

-- GET /clubs/{club_id}/members
SELECT u.id, u.full_name, u.email, cm.role_in_club, cm.status
FROM club_memberships cm JOIN users u ON u.id = cm.user_id
WHERE cm.club_id = :club_id AND cm.status = 'approved';

-- POST /clubs/{club_id}/membership-requests  (submit a membership request)
INSERT INTO club_memberships (user_id, club_id, role_in_club, status, applied_at)
VALUES (:user_id, :club_id, 'member', 'pending', CURRENT_TIMESTAMP);

-- PATCH /memberships/{membership_id}/approve
UPDATE club_memberships
SET status = 'approved', decided_at = CURRENT_TIMESTAMP, approved_by = :approver_id
WHERE id = :membership_id;

-- PATCH /memberships/{membership_id}/reject
UPDATE club_memberships
SET status = 'rejected', decided_at = CURRENT_TIMESTAMP, approved_by = :approver_id,
    rejection_reason = :reason
WHERE id = :membership_id;

-- GET /events?upcoming=true
SELECT id, club_id, title, start_at, end_at, venue, status
FROM events WHERE start_at > CURRENT_TIMESTAMP ORDER BY start_at;

-- GET /events/{event_id}
SELECT id, club_id, title, description, venue, start_at, end_at, capacity, status
FROM events WHERE id = :event_id;

-- POST /events/{event_id}/register  (register for an event)
INSERT INTO event_registrations (event_id, user_id, status, registered_at)
VALUES (:event_id, :user_id, 'registered', CURRENT_TIMESTAMP);

-- POST /events/{event_id}/attendance  (record attendance / check-in)
INSERT INTO attendance_records (event_id, user_id, checked_in_at, recorded_by)
VALUES (:event_id, :user_id, CURRENT_TIMESTAMP, :recorded_by);

-- GET /events/{event_id}/attendance-summary
SELECT
  (SELECT COUNT(*) FROM event_registrations WHERE event_id = :event_id) AS registered_count,
  (SELECT COUNT(*) FROM attendance_records WHERE event_id = :event_id) AS attended_count;

-- GET /budgets/{club_id}
SELECT id, title, period_start, period_end, allocated_amount, status
FROM budgets WHERE club_id = :club_id;

-- GET /expenses?status=pending
SELECT id, budget_id, description, amount, submitted_by, approval_status
FROM expenses WHERE approval_status = :status;

-- PATCH /expenses/{expense_id}/approve
UPDATE expenses
SET approval_status = 'approved', status = 'approved',
    approved_by = :approver_id, approval_date = CURRENT_TIMESTAMP, approval_remarks = :remarks
WHERE id = :expense_id;

-- PATCH /expenses/{expense_id}/reject
UPDATE expenses
SET approval_status = 'rejected', status = 'rejected',
    approved_by = :approver_id, approval_date = CURRENT_TIMESTAMP, approval_remarks = :remarks
WHERE id = :expense_id;

-- GET /users/{user_id}/notifications?unread=true
SELECT id, type, title, body, created_at
FROM notifications WHERE user_id = :user_id AND is_read = 0
ORDER BY created_at DESC;

-- PATCH /notifications/{notification_id}/read
UPDATE notifications SET is_read = 1 WHERE id = :notification_id;

-- GET /support-tickets/{ticket_id}/responses
SELECT r.id, r.responder_id, r.body, r.is_resolution, r.created_at
FROM ticket_responses r WHERE r.ticket_id = :ticket_id ORDER BY r.created_at;

-- POST /support-tickets/{ticket_id}/responses  (post a helpdesk reply)
INSERT INTO ticket_responses (ticket_id, responder_id, body, is_resolution, created_at)
VALUES (:ticket_id, :responder_id, :body, :is_resolution, CURRENT_TIMESTAMP);

-- GET /users/{user_id}/reward-balance
SELECT COALESCE(SUM(points), 0) AS balance FROM reward_points_ledger WHERE user_id = :user_id;

-- GET /sponsors/{sponsor_id}/clubs
SELECT c.id, c.name FROM club_sponsors cs JOIN clubs c ON c.id = cs.club_id
WHERE cs.sponsor_id = :sponsor_id;

-- GET /users/{user_id}/profile  (student academic profile)
SELECT sp.academic_year, sp.semester, sp.batch, sp.section, p.name AS program, d.name AS department
FROM student_profiles sp
JOIN programs p ON p.id = sp.program_id
JOIN departments d ON d.id = p.department_id
WHERE sp.user_id = :user_id;

-- GET /users/{user_id}/interests
SELECT i.id, i.name FROM user_interests ui JOIN interests i ON i.id = ui.interest_id
WHERE ui.user_id = :user_id;

-- POST /users/{user_id}/interests  (add an interest)
INSERT INTO user_interests (user_id, interest_id, created_at) VALUES (:user_id, :interest_id, CURRENT_TIMESTAMP);

-- GET /clubs/{club_id}/interests
SELECT i.id, i.name FROM club_interests ci JOIN interests i ON i.id = ci.interest_id
WHERE ci.club_id = :club_id;

-- GET /clubs/recommended?user_id={user_id}
SELECT DISTINCT c.id, c.name FROM club_interests ci JOIN clubs c ON c.id = ci.club_id
WHERE ci.interest_id IN (SELECT interest_id FROM user_interests WHERE user_id = :user_id);

-- POST /clubs/{club_id}/join-applications  (submit a club join application)
INSERT INTO club_join_applications (user_id, club_id, motivation, contribution, status, applied_at)
VALUES (:user_id, :club_id, :motivation, :contribution, 'pending', CURRENT_TIMESTAMP);

-- GET /clubs/{club_id}/join-applications?status=pending
SELECT id, user_id, motivation, applied_at FROM club_join_applications
WHERE club_id = :club_id AND status = :status;

-- PATCH /join-applications/{application_id}/decide
UPDATE club_join_applications
SET status = :status, reviewed_by = :reviewer_id, review_comments = :comments, reviewed_at = CURRENT_TIMESTAMP
WHERE id = :application_id;

-- GET /users/{user_id}/session  (this user's active login session)
SELECT token, expires_at FROM auth_sessions
WHERE user_id = :user_id AND expires_at > CURRENT_TIMESTAMP;

-- POST /auth/logout  (delete the session row for this token)
DELETE FROM auth_sessions WHERE token = :token;
