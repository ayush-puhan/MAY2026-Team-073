-- ClubConnect sample data (fictional). Loads cleanly against a freshly
-- initialized database (all 33 tables). Respects every FK/unique/check
-- constraint defined in the ORM models.

PRAGMA foreign_keys = ON;

-- ============ users (auth.py) ============
-- NOTE: User rows are intentionally NOT inserted here. SQL cannot call
-- Werkzeug's generate_password_hash(), so the 9 sample users (same ids,
-- emails, and roles referenced below — including user 9, a GOOGLE-auth
-- demo user) are created by the Python seed script
-- `python -m database.seed_sample_data`, which inserts real password
-- hashes and then runs the rest of this file. Do not insert placeholder
-- users here or ids will collide with the seed script.

-- ============ auth_sessions (auth.py) ============
-- NOT seeded here. A real JWT can't be constructed in plain SQL (it needs
-- Flask-JWT-Extended + JWT_SECRET_KEY), so `seed_sample_data.py` calls
-- `session_manager.generate_and_store_token()` for a couple of sample
-- users after this script runs, producing genuine tokens instead of fake
-- placeholder values.

-- ============ departments (academics.py) ============
INSERT INTO departments (id, name, code, created_at) VALUES
(1, 'Computer Science & Engineering', 'CSE', '2026-01-01 09:00:00'),
(2, 'Electronics & Communication Engineering', 'ECE', '2026-01-01 09:00:00'),
(3, 'Mechanical Engineering', 'ME', '2026-01-01 09:00:00'),
(4, 'Management Studies', 'MS', '2026-01-01 09:00:00');

-- ============ programs (academics.py) ============
INSERT INTO programs (id, department_id, name, created_at) VALUES
(1, 1, 'B.Tech Computer Science', '2026-01-01 09:00:00'),
(2, 1, 'M.Tech Artificial Intelligence', '2026-01-01 09:00:00'),
(3, 2, 'B.Tech Electronics', '2026-01-01 09:00:00'),
(4, 3, 'B.Tech Mechanical Engineering', '2026-01-01 09:00:00'),
(5, 4, 'MBA', '2026-01-01 09:00:00'),
(6, 1, 'B.Sc Data Science', '2026-01-01 09:00:00');

-- ============ student_profiles (academics.py) ============
INSERT INTO student_profiles (user_id, program_id, academic_year, semester, batch, section, created_at) VALUES
(1, 1, 2, 4, '2024', 'A', '2026-01-10 09:00:00'),
(2, 1, 2, 4, '2024', 'B', '2026-01-10 09:00:00'),
(3, 3, 3, 6, '2023', 'A', '2026-01-10 09:00:00'),
(8, 4, 2, 3, '2024', 'C', '2026-01-10 09:00:00'),
(9, 6, 2, 4, '2024', 'A', '2026-01-10 09:00:00');

-- ============ interests (interests.py) ============
INSERT INTO interests (id, name, created_at) VALUES
(1, 'Artificial Intelligence', '2026-01-01 09:00:00'),
(2, 'Robotics', '2026-01-01 09:00:00'),
(3, 'Photography', '2026-01-01 09:00:00'),
(4, 'Music', '2026-01-01 09:00:00'),
(5, 'Entrepreneurship', '2026-01-01 09:00:00'),
(6, 'Machine Learning', '2026-01-01 09:00:00');

-- ============ user_interests (interests.py) ============
INSERT INTO user_interests (id, user_id, interest_id, created_at) VALUES
(1, 1, 2, '2026-01-11 09:00:00'),
(2, 1, 6, '2026-01-11 09:00:00'),
(3, 3, 3, '2026-02-02 09:00:00'),
(4, 9, 1, '2026-01-15 09:00:00');



-- ============ clubs (clubs.py) ============
INSERT INTO clubs (id, name, slug, category, description, status, faculty_advisor_id, member_count_cache, created_at) VALUES
(1, 'Chess Club', 'chess-club', 'Games', 'Strategy and tournament chess.', 'active', 4, 2, '2026-01-10 12:00:00'),
(2, 'Robotics Society', 'robotics-society', 'Technical', 'Builds and competes with robots.', 'active', 4, 1, '2026-01-11 12:00:00'),
(3, 'Photography Club', 'photography-club', 'Arts', 'Campus photo-walks and exhibitions.', 'pending', NULL, 0, '2026-02-01 09:00:00');

-- ============ club_interests (interests.py) ============
INSERT INTO club_interests (id, club_id, interest_id, created_at) VALUES
(1, 2, 2, '2026-01-11 09:00:00'),
(2, 2, 6, '2026-01-11 09:00:00'),
(3, 3, 3, '2026-02-01 09:00:00');

-- ============ club_creation_requests (clubs.py) ============
INSERT INTO club_creation_requests (id, proposed_name, proposed_category, proposal_description, requested_by, status, reviewed_by, resulting_club_id, created_at, decided_at) VALUES
(1, 'Photography Club', 'Arts', 'A club for amateur and enthusiast photographers.', 3, 'approved', 6, 3, '2026-01-25 10:00:00', '2026-02-01 09:00:00'),
(2, 'Debate Society', 'Literary', 'Weekly debates and MUN prep.', 8, 'submitted', NULL, NULL, '2026-03-01 10:00:00', NULL);

-- ============ club_memberships (clubs.py) ============
INSERT INTO club_memberships (id, user_id, club_id, role_in_club, status, applied_at, decided_at, approved_by, rejection_reason) VALUES
(1, 1, 1, 'president', 'approved', '2026-01-10 12:30:00', '2026-01-11 09:00:00', 4, NULL),
(2, 2, 1, 'member', 'approved', '2026-01-12 12:30:00', '2026-01-13 09:00:00', 4, NULL),
(3, 3, 2, 'member', 'pending', '2026-02-05 12:30:00', NULL, NULL, NULL),
(4, 8, 2, 'member', 'rejected', '2026-02-06 12:30:00', '2026-02-07 09:00:00', 4, 'Membership capacity reached');

-- ============ committees (clubs.py) ============
INSERT INTO committees (id, club_id, name, description, created_at) VALUES
(1, 1, 'Tournament Committee', 'Organizes internal and inter-college tournaments.', '2026-01-15 09:00:00');

-- ============ committee_memberships (clubs.py) ============
INSERT INTO committee_memberships (id, committee_id, membership_id, joined_at) VALUES
(1, 1, 1, '2026-01-15 09:30:00'),
(2, 1, 2, '2026-01-16 09:30:00');

-- ============ announcements (clubs.py) ============
INSERT INTO announcements (id, club_id, posted_by, title, body, target_audience, created_at) VALUES
(1, 1, 4, 'Chess Club Weekly Meet', 'We meet every Friday at 5 PM in Room 204.', 'all_members', '2026-01-20 08:00:00'),
(2, NULL, 6, 'Annual Fest Dates Announced', 'The annual college fest will be held in October.', 'all_students', '2026-02-15 08:00:00');

-- ============ events (events.py) ============
INSERT INTO events (id, club_id, title, description, venue, start_at, end_at, registration_deadline, capacity, status, created_by, requires_external_participants, created_at) VALUES
(1, 1, 'Inter-College Chess Championship', 'Open chess tournament.', 'Main Auditorium', '2026-08-01 09:00:00', '2026-08-01 18:00:00', '2026-07-25 23:59:00', 64, 'scheduled', 4, 1, '2026-06-01 10:00:00'),
(2, 2, 'Robotics Demo Day', 'Showcase of student robotics projects.', 'Engineering Lab 3', '2026-07-20 10:00:00', '2026-07-20 13:00:00', '2026-07-18 23:59:00', 40, 'scheduled', 4, 0, '2026-06-10 10:00:00');

-- ============ event_interests (interests.py) ============
INSERT INTO event_interests (id, event_id, interest_id, created_at) VALUES
(1, 2, 2, '2026-06-10 09:00:00'),
(2, 2, 6, '2026-06-10 09:00:00');

-- ============ event_registrations (events.py) ============
INSERT INTO event_registrations (id, event_id, user_id, registered_at, status) VALUES
(1, 1, 1, '2026-06-15 09:00:00', 'registered'),
(2, 1, 2, '2026-06-16 09:00:00', 'registered'),
(3, 2, 3, '2026-06-20 09:00:00', 'registered');

-- ============ attendance_records (events.py) ============
-- Note: user_id 2 registered for event 1 but has NO attendance row (no-show).
INSERT INTO attendance_records (id, event_id, user_id, checked_in_at, recorded_by) VALUES
(1, 1, 1, '2026-08-01 09:05:00', 4);

-- ============ volunteer_assignments (events.py) ============
INSERT INTO volunteer_assignments (id, event_id, assignee_membership_id, assigned_by, task_description, status, due_at, created_at) VALUES
(1, 1, 2, 4, 'Manage registration desk on tournament day.', 'assigned', '2026-08-01 08:00:00', '2026-06-20 10:00:00');

-- ============ external_participants (events.py) ============
INSERT INTO external_participants (id, event_id, full_name, email, affiliation, participant_type, registered_at) VALUES
(1, 1, 'Grandmaster Vikram Rao', 'vikram.rao@chessfed.org', 'National Chess Federation', 'guest_speaker', '2026-06-05 09:00:00');

-- ============ budgets (finance.py) ============
INSERT INTO budgets (id, club_id, title, period_start, period_end, allocated_amount, status, created_by, created_at) VALUES
(1, 1, 'Chess Club FY26 Budget', '2026-01-01 00:00:00', '2026-12-31 00:00:00', 15000.00, 'approved', 4, '2026-01-05 10:00:00'),
(2, 2, 'Robotics Society FY26 Budget', '2026-01-01 00:00:00', '2026-12-31 00:00:00', 40000.00, 'submitted', 4, '2026-01-06 10:00:00');

-- ============ documents (communication.py) ============
INSERT INTO documents (id, owner_id, club_id, event_id, doc_type, file_url, title, created_at) VALUES
(1, 4, 1, NULL, 'general', 'https://storage.example.com/docs/chess-constitution.pdf', 'Chess Club Constitution', '2026-01-08 09:00:00'),
(2, 1, 1, 1, 'receipt', 'https://storage.example.com/docs/receipt-001.pdf', 'Trophy Purchase Receipt', '2026-07-10 09:00:00'),
(3, 4, 1, 1, 'certificate', 'https://storage.example.com/docs/cert-priya.pdf', 'Champion Certificate - Priya Sharma', '2026-08-02 09:00:00'),
(4, 9, NULL, NULL, 'general', 'https://storage.example.com/docs/resume-kavya.pdf', 'Kavya Iyer - Resume', '2026-01-19 09:00:00');

-- ============ expenses (finance.py) ============
INSERT INTO expenses (id, budget_id, description, amount, category, receipt_document_id, submitted_by, status, approval_status, approved_by, approval_date, approval_remarks, created_at) VALUES
(1, 1, 'Trophies and medals for championship', 4500.00, 'Equipment', 2, 1, 'approved', 'approved', 4, '2026-07-11 09:00:00', 'Within budget, approved.', '2026-07-09 09:00:00'),
(2, 2, 'Arduino kits for robotics workshop', 12000.00, 'Equipment', NULL, 2, 'pending', 'pending', NULL, NULL, NULL, '2026-07-12 09:00:00'),
(3, 1, 'Venue decoration', 1800.00, 'Miscellaneous', NULL, 1, 'rejected', 'rejected', 4, '2026-07-13 09:00:00', 'Not essential for this event.', '2026-07-12 12:00:00');

-- ============ notifications (communication.py) ============
INSERT INTO notifications (id, user_id, type, title, body, channel, is_read, sent_via_resend, related_entity_type, related_entity_id, created_at) VALUES
(1, 1, 'membership_update', 'Membership Approved', 'Your membership to Chess Club has been approved.', 'in_app', 1, 0, 'club_membership', 1, '2026-01-11 09:05:00'),
(2, 3, 'membership_update', 'Membership Pending', 'Your membership request to Robotics Society is pending review.', 'in_app', 0, 0, 'club_membership', 3, '2026-02-05 12:35:00'),
(3, 1, 'event_reminder', 'Event Tomorrow', 'Inter-College Chess Championship starts tomorrow.', 'both', 0, 1, 'event', 1, '2026-07-31 09:00:00');

-- ============ support_tickets (support.py) ============
INSERT INTO support_tickets (id, raised_by, club_id, title, description, assigned_agent_id, is_open, is_offensive, resolution_rating, created_at) VALUES
(1, 8, NULL, 'Cannot reset password', 'The password reset email never arrives.', 6, 1, 0, NULL, '2026-06-01 10:00:00'),
(2, 3, 2, 'Membership stuck in pending', 'My membership request has been pending for 2 weeks.', 6, 0, 0, 4, '2026-05-15 10:00:00');

-- ============ ticket_responses (support.py) ============
INSERT INTO ticket_responses (id, ticket_id, responder_id, body, is_resolution, created_at) VALUES
(1, 1, 6, 'Please check your spam folder; resending the email now.', 0, '2026-06-01 11:00:00'),
(2, 2, 6, 'Followed up with the club advisor; status updated.', 1, '2026-05-20 09:00:00');

-- ============ emergency_reports (support.py) ============
INSERT INTO emergency_reports (id, reported_by, event_id, category, description, status, handled_by, created_at, resolved_at) VALUES
(1, 3, 2, 'medical', 'A participant fainted during the robotics demo.', 'resolved', 5, '2026-07-20 11:00:00', '2026-07-20 11:30:00'),
(2, NULL, NULL, 'wheelchair_assistance', 'Wheelchair access requested for the auditorium entrance.', 'reported', NULL, '2026-07-25 09:00:00', NULL);

-- ============ reward_points_ledger (rewards.py) ============
INSERT INTO reward_points_ledger (id, user_id, points, reason, source_event_id, created_at) VALUES
(1, 1, 100, 'Won chess championship', 1, '2026-08-02 09:00:00'),
(2, 2, 20, 'Volunteered at registration desk', 1, '2026-08-01 19:00:00'),
(3, 1, -30, 'Redeemed for cafeteria voucher', NULL, '2026-08-05 09:00:00');

-- ============ reward_redemptions (rewards.py) ============
INSERT INTO reward_redemptions (id, user_id, points_spent, reward_description, status, approved_by, created_at) VALUES
(1, 1, 30, 'Cafeteria Voucher (INR 200)', 'fulfilled', 6, '2026-08-05 09:00:00'),
(2, 2, 15, 'Campus Store Discount Coupon', 'requested', NULL, '2026-08-06 09:00:00');

-- ============ sponsors (external_relations.py) ============
INSERT INTO sponsors (id, organization_name, contact_email, contact_person, created_at) VALUES
(1, 'TechNova Pvt Ltd', 'partnerships@technova.example.com', 'Karan Mehra', '2026-03-01 09:00:00'),
(2, 'Campus Cafe', 'owner@campuscafe.example.com', 'Sunita Verma', '2026-03-05 09:00:00');

-- ============ club_sponsors (external_relations.py) ============
-- TechNova sponsors two different clubs (one sponsor, multiple clubs).
INSERT INTO club_sponsors (id, club_id, sponsor_id, sponsorship_details) VALUES
(1, 1, 1, 'Cash sponsorship of INR 10,000 for the championship.'),
(2, 2, 1, 'Equipment sponsorship: 5 Arduino starter kits.'),
(3, 1, 2, 'Free refreshments during the tournament.');

-- ============ club_join_applications (applications.py) ============
-- One pending, one approved (with resume + reviewer), one rejected.
INSERT INTO club_join_applications (id, user_id, club_id, motivation, contribution, previous_experience, skills, portfolio_url, resume_document_id, weekly_availability, status, reviewed_by, review_comments, applied_at, reviewed_at) VALUES
(1, 3, 2, 'Interested in building autonomous robots.', 'Can help with firmware and sensors.', 'Built a line-follower bot in school.', 'C++, Arduino', NULL, NULL, '5 hrs/week', 'pending', NULL, NULL, '2026-02-05 12:00:00', NULL),
(2, 9, 2, 'Want to apply ML to robot navigation.', 'Can train perception models.', 'Kaggle competitions, one publication.', 'Python, PyTorch', 'https://portfolio.example.com/kavya', 4, '6 hrs/week', 'approved', 4, 'Strong ML background, welcome aboard.', '2026-01-20 10:00:00', '2026-01-22 09:00:00'),
(3, 8, 2, 'Curious about robotics.', 'Limited experience so far.', NULL, NULL, NULL, NULL, '2 hrs/week', 'rejected', 4, 'Membership capacity reached for this cycle.', '2026-02-06 12:00:00', '2026-02-07 09:00:00');

-- ============ application_interests (applications.py) ============
-- Application 2 lists multiple interests.
INSERT INTO application_interests (id, application_id, interest_id) VALUES
(1, 1, 2),
(2, 2, 2),
(3, 2, 6),
(4, 2, 1);
