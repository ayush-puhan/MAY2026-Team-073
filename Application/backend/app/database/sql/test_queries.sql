-- ClubConnect practical read queries. Run against a database that has been
-- initialized (init_db) and loaded with sample_data.sql.

-- 1. List all users
SELECT id, full_name, email, role FROM users;

-- 2. Find a user by email
SELECT id, full_name, role FROM users WHERE email = 'priya.sharma@campus.edu';

-- 3. List all clubs with status
SELECT id, name, status FROM clubs;

-- 4. List approved members of a club
SELECT u.full_name, cm.role_in_club
FROM club_memberships cm JOIN users u ON u.id = cm.user_id
WHERE cm.club_id = 1 AND cm.status = 'approved';

-- 5. List pending membership requests
SELECT u.full_name, c.name AS club_name, cm.applied_at
FROM club_memberships cm
JOIN users u ON u.id = cm.user_id
JOIN clubs c ON c.id = cm.club_id
WHERE cm.status = 'pending';

-- 6. Show clubs joined (approved) by a specific user
SELECT c.name, cm.role_in_club
FROM club_memberships cm JOIN clubs c ON c.id = cm.club_id
WHERE cm.user_id = 1 AND cm.status = 'approved';

-- 7. Show committees and their members
SELECT co.name AS committee_name, u.full_name
FROM committee_memberships cme
JOIN committees co ON co.id = cme.committee_id
JOIN club_memberships cm ON cm.id = cme.membership_id
JOIN users u ON u.id = cm.user_id;

-- 8. List club announcements (most recent first)
SELECT title, target_audience, created_at FROM announcements ORDER BY created_at DESC;

-- 9. List upcoming events
SELECT title, start_at, venue FROM events WHERE start_at > CURRENT_TIMESTAMP;

-- 10. List event registrations for an event
SELECT u.full_name, er.status
FROM event_registrations er JOIN users u ON u.id = er.user_id
WHERE er.event_id = 1;

-- 11. List actual attendees of an event
SELECT u.full_name, ar.checked_in_at
FROM attendance_records ar JOIN users u ON u.id = ar.user_id
WHERE ar.event_id = 1;

-- 12. Find registered users who did NOT attend (no-shows)
SELECT u.full_name
FROM event_registrations er JOIN users u ON u.id = er.user_id
WHERE er.event_id = 1
  AND er.user_id NOT IN (SELECT user_id FROM attendance_records WHERE event_id = er.event_id);

-- 13. Show volunteers assigned to an event
SELECT u.full_name, va.task_description, va.status
FROM volunteer_assignments va
JOIN club_memberships cm ON cm.id = va.assignee_membership_id
JOIN users u ON u.id = cm.user_id
WHERE va.event_id = 1;

-- 14. Show external participants for an event
SELECT full_name, participant_type, affiliation FROM external_participants WHERE event_id = 1;

-- 15. Show budgets and their remaining balance vs approved expenses
SELECT b.title, b.allocated_amount,
       COALESCE(SUM(CASE WHEN e.approval_status = 'approved' THEN e.amount ELSE 0 END), 0) AS spent
FROM budgets b LEFT JOIN expenses e ON e.budget_id = b.id
GROUP BY b.id;

-- 16. Show pending expense approvals
SELECT description, amount, category FROM expenses WHERE approval_status = 'pending';

-- 17. Show an expense with submitter, approver, and receipt document
SELECT ex.description, ex.amount,
       submitter.full_name AS submitted_by,
       approver.full_name AS approved_by,
       doc.title AS receipt
FROM expenses ex
JOIN users submitter ON submitter.id = ex.submitted_by
LEFT JOIN users approver ON approver.id = ex.approved_by
LEFT JOIN documents doc ON doc.id = ex.receipt_document_id
WHERE ex.id = 1;

-- 18. Show documents linked to a club
SELECT title, doc_type, created_at FROM documents WHERE club_id = 1;

-- 19. Show unread notifications for a user
SELECT title, body, created_at FROM notifications WHERE user_id = 1 AND is_read = 0;

-- 20. Show support tickets with full response history
SELECT t.title, t.status, r.body, r.is_resolution, r.created_at
FROM support_tickets t LEFT JOIN ticket_responses r ON r.ticket_id = t.id
WHERE t.id = 1
ORDER BY r.created_at;

-- 21. List all open support tickets
SELECT id, title, raised_by FROM support_tickets WHERE status = 'Open';

-- 22. Show unresolved emergency reports
SELECT category, description, created_at FROM emergency_reports WHERE status != 'resolved';

-- 23. Calculate a user's reward point balance
SELECT user_id, SUM(points) AS balance FROM reward_points_ledger WHERE user_id = 1 GROUP BY user_id;

-- 24. Show pending reward redemptions
SELECT u.full_name, rr.reward_description, rr.points_spent
FROM reward_redemptions rr JOIN users u ON u.id = rr.user_id
WHERE rr.status = 'requested';

-- 25. Show sponsors for a specific club
SELECT s.organization_name, cs.sponsorship_details
FROM club_sponsors cs JOIN sponsors s ON s.id = cs.sponsor_id
WHERE cs.club_id = 1;

-- 26. Show all clubs supported by a specific sponsor
SELECT c.name, cs.sponsorship_details
FROM club_sponsors cs JOIN clubs c ON c.id = cs.club_id
WHERE cs.sponsor_id = 1;

-- 27. Count club members per club
SELECT c.name, COUNT(cm.id) AS approved_members
FROM clubs c LEFT JOIN club_memberships cm ON cm.club_id = c.id AND cm.status = 'approved'
GROUP BY c.id;

-- 28. List club creation requests awaiting review
SELECT proposed_name, requested_by, status FROM club_creation_requests WHERE status IN ('submitted', 'under_review');

-- 29. Show a user's current login session
SELECT token, created_at, expires_at FROM auth_sessions WHERE user_id = 1;

-- 30. Show events created by a specific advisor
SELECT title, start_at, status FROM events WHERE created_by = 4;

-- 31. Show all expenses for a club (via budgets)
SELECT ex.description, ex.amount, ex.approval_status
FROM expenses ex JOIN budgets b ON b.id = ex.budget_id
WHERE b.club_id = 1;

-- 32. Find a club by slug
SELECT id, name, status FROM clubs WHERE slug = 'chess-club';

-- 33. Show all committee members' committee assignments for a user
SELECT co.name AS committee_name
FROM committee_memberships cme
JOIN committees co ON co.id = cme.committee_id
JOIN club_memberships cm ON cm.id = cme.membership_id
WHERE cm.user_id = 1;

-- 34. Show notification counts by type for a user
SELECT type, COUNT(*) FROM notifications WHERE user_id = 1 GROUP BY type;

-- 35. Show soft-deleted (deactivated) users, if any
SELECT id, full_name FROM users WHERE deleted_at IS NOT NULL;

-- 36. List programs by department
SELECT p.name AS program, d.name AS department FROM programs p JOIN departments d ON d.id = p.department_id;

-- 37. Show a student's academic profile
SELECT u.full_name, p.name AS program, sp.academic_year, sp.semester, sp.batch, sp.section
FROM student_profiles sp
JOIN users u ON u.id = sp.user_id
JOIN programs p ON p.id = sp.program_id
WHERE sp.user_id = 1;

-- 38. Show a user's declared interests
SELECT i.name FROM user_interests ui JOIN interests i ON i.id = ui.interest_id WHERE ui.user_id = 1;

-- 39. Show a club's declared interests
SELECT i.name FROM club_interests ci JOIN interests i ON i.id = ci.interest_id WHERE ci.club_id = 2;

-- 40. Show an event's topics (event-specific interests)
SELECT i.name FROM event_interests ei JOIN interests i ON i.id = ei.interest_id WHERE ei.event_id = 2;

-- 41. Recommend clubs sharing at least one interest with a user
SELECT DISTINCT c.name
FROM club_interests ci
JOIN clubs c ON c.id = ci.club_id
WHERE ci.interest_id IN (SELECT interest_id FROM user_interests WHERE user_id = 1);

-- 42. Show pending club join applications for review
SELECT u.full_name, c.name AS club_name, a.applied_at
FROM club_join_applications a
JOIN users u ON u.id = a.user_id
JOIN clubs c ON c.id = a.club_id
WHERE a.status = 'pending';

-- 43. Show a club join application with reviewer and resume
SELECT a.motivation, a.status,
       reviewer.full_name AS reviewed_by,
       doc.title AS resume
FROM club_join_applications a
LEFT JOIN users reviewer ON reviewer.id = a.reviewed_by
LEFT JOIN documents doc ON doc.id = a.resume_document_id
WHERE a.id = 2;

-- 44. Show the interests listed on a club join application
SELECT i.name
FROM application_interests ai
JOIN interests i ON i.id = ai.interest_id
WHERE ai.application_id = 2;

-- 45. Show active (non-expired) JWT sessions
SELECT user_id, expires_at
FROM auth_sessions
WHERE expires_at > CURRENT_TIMESTAMP;

-- 46. Show expired JWT sessions still awaiting cleanup
SELECT user_id, expires_at FROM auth_sessions WHERE expires_at <= CURRENT_TIMESTAMP;
