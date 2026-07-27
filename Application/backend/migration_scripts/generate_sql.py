import json
import os
import sqlite3

FRONTEND_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'db.json'))
OUTPUT_SQL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'seed_data.sql'))
SQLITE_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'database', 'clubconnect.db'))

def escape(val):
    if val is None: return "NULL"
    if isinstance(val, bool): return "1" if val else "0"
    if isinstance(val, (int, float)): return str(val)
    return f"'{str(val).replace(chr(39), chr(39)+chr(39))}'"

def g(d, key, default=None):
    return d.get(key, default)

def generate_sql():
    with open(FRONTEND_DB, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    lines.append("PRAGMA foreign_keys = OFF;")
    lines.append("BEGIN TRANSACTION;")

    # 1. Universities
    lines.append("DELETE FROM universities;")
    for u in data.get("universities", []):
        domain = g(u, "domain", f"{g(u, 'name', 'Univ').split()[0].lower()}.edu")
        lines.append(f"INSERT OR IGNORE INTO universities (id, name, short_name, logo_url, domain, is_active, created_at) VALUES "
                     f"({escape(g(u, 'id'))}, {escape(g(u, 'name'))}, {escape(g(u, 'short_name', g(u, 'name', 'U').split()[0]))}, "
                     f"{escape(g(u, 'logo_url'))}, {escape(domain)}, 1, CURRENT_TIMESTAMP);")

    # 2. University Domains
    lines.append("DELETE FROM university_domains;")
    for d in data.get("university_domains", []):
        lines.append(f"INSERT OR IGNORE INTO university_domains (id, university_id, domain, created_at) VALUES "
                     f"({escape(g(d, 'id'))}, {escape(g(d, 'university_id'))}, {escape(g(d, 'domain'))}, CURRENT_TIMESTAMP);")

    # 3. Departments
    lines.append("DELETE FROM departments;")
    for d in data.get("departments", []):
        lines.append(f"INSERT OR IGNORE INTO departments (id, name, code, university_id, created_at) VALUES "
                     f"({escape(g(d, 'id'))}, {escape(g(d, 'name'))}, {escape(g(d, 'code'))}, {escape(g(d, 'university_id'))}, CURRENT_TIMESTAMP);")

    # 4. Programs
    lines.append("DELETE FROM programs;")
    for p in data.get("programs", []):
        lines.append(f"INSERT OR IGNORE INTO programs (id, department_id, name, created_at) VALUES "
                     f"({escape(g(p, 'id'))}, {escape(g(p, 'department_id'))}, {escape(g(p, 'name'))}, CURRENT_TIMESTAMP);")

    # 5. Interests
    lines.append("DELETE FROM interests;")
    for i in data.get("interests", []):
        lines.append(f"INSERT OR IGNORE INTO interests (id, name, created_at) VALUES "
                     f"({escape(g(i, 'id'))}, {escape(g(i, 'name'))}, CURRENT_TIMESTAMP);")

    # 6. Sponsors
    lines.append("DELETE FROM sponsors;")
    for s in data.get("sponsors", []):
        org_name = g(s, "name", g(s, "organization_name", "Unknown Sponsor"))
        lines.append(f"INSERT OR IGNORE INTO sponsors (id, organization_name, contact_email, contact_person, created_at) VALUES "
                     f"({escape(g(s, 'id'))}, {escape(org_name)}, {escape(g(s, 'contact_email'))}, {escape(g(s, 'contact_person'))}, CURRENT_TIMESTAMP);")

    # 7. Users
    lines.append("DELETE FROM users;")
    import bcrypt
    for u in data.get("users", []):
        raw_pw = str(g(u, "password_hash", "Password@123")).encode('utf-8')
        hashed = bcrypt.hashpw(raw_pw, bcrypt.gensalt()).decode('utf-8')
        role = str(g(u, "role", "STUDENT")).upper()
        auth_provider = str(g(u, "auth_provider", "LOCAL")).upper()
        gender = str(g(u, "gender", "OTHER")).upper() if g(u, "gender") else None
        lines.append(f"INSERT OR IGNORE INTO users (id, email, password_hash, full_name, roll_number, role, phone, profile_photo_url, "
                     f"accessibility_prefs, is_active, email_verified, google_id, dob, auth_provider, department_id, university_id, "
                     f"gender, color_blind_mode, created_at) VALUES "
                     f"({escape(g(u, 'id'))}, {escape(g(u, 'email'))}, {escape(hashed)}, {escape(g(u, 'full_name'))}, {escape(g(u, 'roll_number'))}, "
                     f"{escape(role)}, {escape(g(u, 'phone'))}, {escape(g(u, 'profile_photo_url'))}, {escape(g(u, 'accessibility_prefs'))}, "
                     f"{escape(g(u, 'is_active', True))}, {escape(g(u, 'email_verified', True))}, {escape(g(u, 'google_id'))}, "
                     f"{escape(g(u, 'dob'))}, {escape(auth_provider)}, {escape(g(u, 'department_id'))}, {escape(g(u, 'university_id'))}, "
                     f"{escape(gender)}, {escape(g(u, 'color_blind_mode', False))}, CURRENT_TIMESTAMP);")

    # 8. Student Profiles
    lines.append("DELETE FROM student_profiles;")
    for sp in data.get("student_profiles", []):
        lines.append(f"INSERT OR IGNORE INTO student_profiles (user_id, program_id, academic_year, semester, batch, section, institutional_email, is_verified, created_at) VALUES "
                     f"({escape(g(sp, 'user_id'))}, {escape(g(sp, 'program_id', 1))}, {escape(g(sp, 'year_of_study', 1))}, NULL, NULL, NULL, NULL, 0, CURRENT_TIMESTAMP);")

    # 9. User Interests
    lines.append("DELETE FROM user_interests;")
    for ui in data.get("user_interests", []):
        lines.append(f"INSERT OR IGNORE INTO user_interests (id, user_id, interest_id, created_at) VALUES "
                     f"({escape(g(ui, 'id'))}, {escape(g(ui, 'user_id'))}, {escape(g(ui, 'interest_id'))}, CURRENT_TIMESTAMP);")

    # 10. Clubs
    lines.append("DELETE FROM clubs;")
    for c in data.get("clubs", []):
        status = str(g(c, "status", "ACTIVE")).upper()
        lines.append(f"INSERT OR IGNORE INTO clubs (id, name, slug, description, logo_url, banner, status, faculty_advisor_id, university_id, member_count_cache, created_at) VALUES "
                     f"({escape(g(c, 'id'))}, {escape(g(c, 'name'))}, {escape(g(c, 'name', 'club').lower().replace(' ', '-'))}, {escape(g(c, 'description'))}, {escape(g(c, 'logo_url'))}, {escape(g(c, 'banner_url'))}, "
                     f"{escape(status)}, {escape(g(c, 'faculty_advisor_id'))}, {escape(g(c, 'university_id'))}, 0, CURRENT_TIMESTAMP);")

    # 11. Club Creation Requests
    lines.append("DELETE FROM club_creation_requests;")
    for r in data.get("club_creation_requests", []):
        status = str(g(r, "status", "SUBMITTED")).upper()
        req_by = g(r, 'requested_by', g(r, 'requester_id', g(r, 'applicant_id', 1)))
        desc = g(r, 'proposal_description', g(r, 'proposed_description', 'No description'))
        lines.append(f"INSERT OR IGNORE INTO club_creation_requests (id, requested_by, proposed_name, proposal_description, faculty_advisor_id, status, review_comments, created_at) VALUES "
                     f"({escape(g(r, 'id'))}, {escape(req_by)}, {escape(g(r, 'proposed_name'))}, {escape(desc)}, "
                     f"{escape(g(r, 'faculty_advisor_id'))}, {escape(status)}, {escape(g(r, 'review_comments'))}, CURRENT_TIMESTAMP);")

    # 12. Club Interests
    lines.append("DELETE FROM club_interests;")
    for ci in data.get("club_interests", []):
        lines.append(f"INSERT OR IGNORE INTO club_interests (id, club_id, interest_id, created_at) VALUES "
                     f"({escape(g(ci, 'id'))}, {escape(g(ci, 'club_id'))}, {escape(g(ci, 'interest_id'))}, CURRENT_TIMESTAMP);")

    # 13. Club Sponsors
    lines.append("DELETE FROM club_sponsors;")
    for cs in data.get("club_sponsors", []):
        details = f"{g(cs, 'sponsorship_type', 'FINANCIAL')} - ${g(cs, 'amount', 0)}"
        lines.append(f"INSERT OR IGNORE INTO club_sponsors (id, club_id, event_id, sponsor_id, sponsorship_details) VALUES "
                     f"({escape(g(cs, 'id'))}, {escape(g(cs, 'club_id'))}, NULL, {escape(g(cs, 'sponsor_id'))}, {escape(details)});")

    # 14. Club Memberships
    lines.append("DELETE FROM club_memberships;")
    for cm in data.get("club_memberships", []):
        role = str(g(cm, "role", "MEMBER")).upper()
        lines.append(f"INSERT OR IGNORE INTO club_memberships (id, user_id, club_id, role_in_club, status, applied_at) VALUES "
                     f"({escape(g(cm, 'id'))}, {escape(g(cm, 'user_id'))}, {escape(g(cm, 'club_id'))}, {escape(role)}, 'APPROVED', {escape(g(cm, 'joined_at', 'CURRENT_TIMESTAMP'))});")

    # 15. Club Join Applications
    lines.append("DELETE FROM club_join_applications;")
    for cja in data.get("club_join_applications", []):
        status = str(g(cja, "status", "PENDING")).upper()
        lines.append(f"INSERT OR IGNORE INTO club_join_applications (id, user_id, club_id, motivation, status, reviewed_by, applied_at) VALUES "
                     f"({escape(g(cja, 'id'))}, {escape(g(cja, 'user_id'))}, {escape(g(cja, 'club_id'))}, {escape(g(cja, 'statement_of_purpose'))}, "
                     f"{escape(status)}, {escape(g(cja, 'reviewed_by'))}, CURRENT_TIMESTAMP);")

    # 16. Committees
    lines.append("DELETE FROM committees;")
    for c in data.get("committees", []):
        lines.append(f"INSERT OR IGNORE INTO committees (id, club_id, name, description) VALUES "
                     f"({escape(g(c, 'id'))}, {escape(g(c, 'club_id'))}, {escape(g(c, 'name'))}, {escape(g(c, 'description'))});")

    # 17. Committee Memberships
    lines.append("DELETE FROM committee_memberships;")
    for cm in data.get("committee_memberships", []):
        role = str(g(cm, "role", "MEMBER")).upper()
        lines.append(f"INSERT OR IGNORE INTO committee_memberships (id, membership_id, committee_id, role, joined_at) VALUES "
                     f"({escape(g(cm, 'id'))}, {escape(g(cm, 'membership_id'))}, {escape(g(cm, 'committee_id'))}, {escape(role)}, {escape(g(cm, 'joined_at', 'CURRENT_TIMESTAMP'))});")

    # 18. Events
    lines.append("DELETE FROM events;")
    for e in data.get("events", []):
        event_type = str(g(e, "event_type", "IN_PERSON")).upper()
        status = str(g(e, "status", "PUBLISHED")).upper()
        lines.append(f"INSERT OR IGNORE INTO events (id, club_id, title, description, banner, venue, start_at, end_at, capacity, status, created_by, created_at) VALUES "
                     f"({escape(g(e, 'id'))}, {escape(g(e, 'club_id'))}, {escape(g(e, 'title'))}, {escape(g(e, 'description'))}, {escape(g(e, 'banner_url'))}, "
                     f"{escape(g(e, 'venue'))}, {escape(g(e, 'start_time', '2026-07-27 10:00:00'))}, {escape(g(e, 'end_time', '2026-07-27 12:00:00'))}, {escape(g(e, 'capacity'))}, {escape(status)}, {escape(g(e, 'organizer_id'))}, CURRENT_TIMESTAMP);")

    # 19. Event Sessions
    lines.append("DELETE FROM event_sessions;")
    for es in data.get("event_sessions", []):
        lines.append(f"INSERT OR IGNORE INTO event_sessions (id, event_id, title, start_at, end_at, description, session_order, venue, created_at) VALUES "
                     f"({escape(g(es, 'id'))}, {escape(g(es, 'event_id'))}, {escape(g(es, 'title', 'Main'))}, {escape(g(es, 'start_time', '2026-07-27 10:00:00'))}, {escape(g(es, 'end_time', '2026-07-27 12:00:00'))}, "
                     f"{escape(g(es, 'speaker_name'))}, 1, {escape(g(es, 'venue'))}, CURRENT_TIMESTAMP);")

    # 20. Event Interests
    lines.append("DELETE FROM event_interests;")
    for ei in data.get("event_interests", []):
        lines.append(f"INSERT OR IGNORE INTO event_interests (id, event_id, interest_id, created_at) VALUES "
                     f"({escape(g(ei, 'id'))}, {escape(g(ei, 'event_id'))}, {escape(g(ei, 'interest_id'))}, CURRENT_TIMESTAMP);")

    # 21. Event Registrations
    lines.append("DELETE FROM event_registrations;")
    for er in data.get("event_registrations", []):
        status = str(g(er, "status", "REGISTERED")).upper()
        lines.append(f"INSERT OR IGNORE INTO event_registrations (id, user_id, event_id, status, registered_at) VALUES "
                     f"({escape(g(er, 'id'))}, {escape(g(er, 'user_id'))}, {escape(g(er, 'event_id'))}, {escape(status)}, {escape(g(er, 'registered_at', 'CURRENT_TIMESTAMP'))});")

    # 22. Attendance Records
    lines.append("DELETE FROM attendance_records;")
    for ar in data.get("attendance_records", []):
        lines.append(f"INSERT OR IGNORE INTO attendance_records (id, user_id, event_id, checked_in_at, recorded_by) VALUES "
                     f"({escape(g(ar, 'id'))}, {escape(g(ar, 'user_id'))}, {escape(g(ar, 'event_id'))}, "
                     f"{escape(g(ar, 'check_in_time', 'CURRENT_TIMESTAMP'))}, {escape(g(ar, 'checked_in_by'))});")

    # 23. External Participants
    lines.append("DELETE FROM external_participants;")
    for ep in data.get("external_participants", []):
        lines.append(f"INSERT OR IGNORE INTO external_participants (id, event_id, full_name, email, affiliation, participant_type, registered_at) VALUES "
                     f"({escape(g(ep, 'id'))}, {escape(g(ep, 'event_id'))}, {escape(g(ep, 'full_name'))}, {escape(g(ep, 'email'))}, {escape(g(ep, 'organization'))}, 'GUEST', CURRENT_TIMESTAMP);")

    # 24. Budgets
    lines.append("DELETE FROM budgets;")
    for b in data.get("budgets", []):
        status = str(g(b, "status", "DRAFT")).upper()
        lines.append(f"INSERT OR IGNORE INTO budgets (id, club_id, title, period_start, period_end, allocated_amount, status, created_by, created_at) VALUES "
                     f"({escape(g(b, 'id'))}, {escape(g(b, 'club_id'))}, {escape(g(b, 'academic_year', '2023-2024'))}, '2023-01-01 00:00:00', '2024-01-01 00:00:00', "
                     f"{escape(g(b, 'allocated_amount', 0))}, {escape(status)}, {escape(g(b, 'submitted_by', 1))}, CURRENT_TIMESTAMP);")

    # 25. Expenses
    lines.append("DELETE FROM expenses;")
    for e in data.get("expenses", []):
        status = str(g(e, "status", "PENDING")).upper()
        lines.append(f"INSERT OR IGNORE INTO expenses (id, budget_id, submitted_by, amount, description, status, approval_status, created_at) VALUES "
                     f"({escape(g(e, 'id'))}, {escape(g(e, 'budget_id'))}, {escape(g(e, 'submitted_by', 1))}, {escape(g(e, 'amount'))}, "
                     f"{escape(g(e, 'description'))}, {escape(status)}, {escape(status)}, CURRENT_TIMESTAMP);")

    # 26. Volunteer Assignments
    lines.append("DELETE FROM volunteer_assignments;")
    for va in data.get("volunteer_assignments", []):
        status = str(g(va, "status", "ASSIGNED")).upper()
        # volunteer_assignments model maps user_id to assignee_membership_id
        lines.append(f"INSERT OR IGNORE INTO volunteer_assignments (id, event_id, assignee_membership_id, task_description, status, assigned_by) VALUES "
                     f"({escape(g(va, 'id'))}, {escape(g(va, 'event_id'))}, {escape(g(va, 'user_id'))}, {escape(g(va, 'role_description', 'No description'))}, {escape(status)}, {escape(g(va, 'assigned_by'))});")

    # 27. Documents
    lines.append("DELETE FROM documents;")
    for d in data.get("documents", []):
        doc_type = str(g(d, "document_type", "OTHER")).upper()
        lines.append(f"INSERT OR IGNORE INTO documents (id, club_id, owner_id, title, file_url, doc_type, created_at) VALUES "
                     f"({escape(g(d, 'id'))}, {escape(g(d, 'club_id'))}, {escape(g(d, 'uploader_id', 1))}, {escape(g(d, 'title'))}, {escape(g(d, 'file_url'))}, "
                     f"{escape(doc_type)}, CURRENT_TIMESTAMP);")

    # 28. Announcements
    lines.append("DELETE FROM announcements;")
    for a in data.get("announcements", []):
        audience = str(g(a, "target_audience", "ALL_MEMBERS")).upper()
        lines.append(f"INSERT OR IGNORE INTO announcements (id, title, body, posted_by, target_audience, club_id, created_at) VALUES "
                     f"({escape(g(a, 'id'))}, {escape(g(a, 'title'))}, {escape(g(a, 'content'))}, {escape(g(a, 'author_id'))}, {escape(audience)}, "
                     f"{escape(g(a, 'club_id'))}, CURRENT_TIMESTAMP);")

    # 29. Notifications
    lines.append("DELETE FROM notifications;")
    for n in data.get("notifications", []):
        ntype = str(g(n, "notification_type", "SYSTEM")).upper()
        lines.append(f"INSERT OR IGNORE INTO notifications (id, user_id, title, body, type, is_read, created_at) VALUES "
                     f"({escape(g(n, 'id'))}, {escape(g(n, 'user_id'))}, {escape(g(n, 'title', 'Notice'))}, {escape(g(n, 'message', 'Notice'))}, {escape(ntype)}, "
                     f"{escape(g(n, 'is_read', False))}, CURRENT_TIMESTAMP);")

    # 30. Support Tickets
    lines.append("DELETE FROM support_tickets;")
    for st in data.get("support_tickets", []):
        status = str(g(st, "status", "OPEN")).upper()
        priority = str(g(st, "priority", "MEDIUM")).upper()
        cat = str(g(st, "category", "SUPPORT")).upper()
        lines.append(f"INSERT OR IGNORE INTO support_tickets (id, raised_by, title, description, status, priority, ticket_type, assigned_agent_id, created_at) VALUES "
                     f"({escape(g(st, 'id'))}, {escape(g(st, 'user_id'))}, {escape(g(st, 'subject'))}, {escape(g(st, 'description'))}, {escape(status)}, "
                     f"{escape(priority)}, {escape(cat)}, {escape(g(st, 'assigned_to'))}, CURRENT_TIMESTAMP);")

    # 31. Ticket Responses
    lines.append("DELETE FROM ticket_responses;")
    for tr in data.get("ticket_responses", []):
        lines.append(f"INSERT OR IGNORE INTO ticket_responses (id, ticket_id, responder_id, body, is_resolution, created_at) VALUES "
                     f"({escape(g(tr, 'id'))}, {escape(g(tr, 'ticket_id'))}, {escape(g(tr, 'responder_id'))}, {escape(g(tr, 'response', 'Response body'))}, {escape(g(tr, 'is_internal', False))}, CURRENT_TIMESTAMP);")

    # 32. Emergency Reports
    lines.append("DELETE FROM emergency_reports;")
    for er in data.get("emergency_reports", []):
        status = str(g(er, "status", "REPORTED")).upper()
        inc_type = str(g(er, "incident_type", "OTHER")).upper()
        if inc_type == "INJURY": inc_type = "MEDICAL"
        lines.append(f"INSERT OR IGNORE INTO emergency_reports (id, reported_by, category, description, status, handled_by) VALUES "
                     f"({escape(g(er, 'id'))}, {escape(g(er, 'reporter_id'))}, {escape(inc_type)}, {escape(g(er, 'description', 'No description'))}, {escape(status)}, {escape(g(er, 'resolved_by'))});")

    lines.append("COMMIT;")

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated SQL with {len(lines)} lines at {OUTPUT_SQL}")

if __name__ == "__main__":
    generate_sql()
