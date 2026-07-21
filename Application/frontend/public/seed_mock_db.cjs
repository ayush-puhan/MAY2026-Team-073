const fs = require('fs');
const path = require('path');

const generateDb = () => {
  const db = {
    users: [],
    auth_sessions: [],
    universities: [],
    university_domains: [],
    departments: [],
    programs: [],
    student_profiles: [],
    interests: [],
    user_interests: [],
    clubs: [],
    club_interests: [],
    club_creation_requests: [],
    club_memberships: [],
    committees: [],
    committee_memberships: [],
    announcements: [],
    events: [],
    event_sessions: [],
    event_interests: [],
    event_registrations: [],
    attendance_records: [],
    volunteer_assignments: [],
    external_participants: [],
    budgets: [],
    expenses: [],
    documents: [],
    notifications: [],
    support_tickets: [],
    ticket_responses: [],
    emergency_reports: [],
    reward_points_ledger: [],
    reward_redemptions: [],
    sponsors: [],
    club_sponsors: [],
    club_join_applications: [],
    application_interests: [],
    audit_logs: []
  };

  const now = new Date();
  const timeStr = now.toISOString().slice(0, 19).replace('T', ' ');

  db.universities.push(
    { id: 1, name: 'Indian Institute of Technology Delhi', short_name: 'IITD', logo_url: '/logos/iitd.png', domain: 'iitd.ac.in', address: 'Hauz Khas, New Delhi', website: 'https://iitd.ac.in', banner: 'sports', is_active: true },
    { id: 2, name: 'BITS Pilani', short_name: 'BITS', logo_url: '/logos/bits.png', domain: 'bits-pilani.ac.in', address: 'Pilani, Rajasthan', website: 'https://bits-pilani.ac.in', banner: 'tech', is_active: true }
  );

  db.university_domains.push(
    { id: 1, university_id: 1, domain: 'iitd.ac.in' },
    { id: 2, university_id: 1, domain: 'admin.iitd.ac.in' },
    { id: 3, university_id: 2, domain: 'bits-pilani.ac.in' },
    { id: 4, university_id: 2, domain: 'campus.bits-pilani.ac.in' }
  );

  db.departments.push(
    { id: 1, university_id: 1, name: 'Computer Science & Engineering', code: 'CSE', created_at: timeStr },
    { id: 2, university_id: 1, name: 'Electrical Engineering', code: 'EE', created_at: timeStr },
    { id: 3, university_id: 2, name: 'Mechanical Engineering', code: 'ME', created_at: timeStr },
    { id: 4, university_id: 2, name: 'Chemical Engineering', code: 'CHE', created_at: timeStr }
  );

  db.programs.push(
    { id: 1, department_id: 1, name: 'B.Tech Computer Science', created_at: timeStr },
    { id: 2, department_id: 2, name: 'B.Tech Electrical', created_at: timeStr },
    { id: 3, department_id: 3, name: 'B.E. Mechanical', created_at: timeStr },
    { id: 4, department_id: 4, name: 'B.E. Chemical', created_at: timeStr }
  );

  for (let i = 1; i <= 20; i++) {
    const uniId = (i % 2) + 1; // Distribute users across universities
    const deptId = uniId === 1 ? (i % 2 === 0 ? 1 : 2) : (i % 2 === 0 ? 3 : 4);
    
    db.users.push({ 
      id: i, 
      email: `user${i}@campus.edu`, 
      password_hash: 'Password@123',
      full_name: `User ${i}`, 
      roll_number: `CS2023${i.toString().padStart(3, '0')}`, 
      role: i === 4 ? "faculty_advisor" : i === 5 ? "system_admin" : "student",
      phone: `+919876543${i.toString().padStart(3, '0')}`,
      profile_photo_url: `/avatars/user${i}.png`,
      accessibility_prefs: '{"high_contrast": false}',
      is_active: true,
      email_verified: true,
      google_id: `g_mock_${i}`,
      dob: '2002-01-01',
      auth_provider: 'LOCAL',
      department_id: deptId,
      university_id: uniId, 
      gender: i % 2 === 0 ? 'MALE' : 'FEMALE',
      color_blind_mode: false
    });

    db.student_profiles.push({ 
      user_id: i, 
      program_id: deptId, 
      academic_year: 2, 
      semester: 4, 
      batch: '2024', 
      section: i % 2 === 0 ? 'A' : 'B', 
      institutional_email: uniId === 1 ? `user${i}@iitd.ac.in` : `user${i}@bits-pilani.ac.in`, 
      is_verified: true,
      created_at: timeStr
    });

    db.auth_sessions.push({ 
      id: i, 
      user_id: i, 
      token: `session_token_${i}`, 
      expires_at: new Date(now.getTime() + 24*60*60*1000).toISOString().slice(0, 19).replace('T', ' ')
    });
  }

  const interestNames = ['Artificial Intelligence', 'Robotics', 'Photography', 'Music', 'Entrepreneurship', 'Machine Learning', 'Sports', 'Technical', 'Cultural', 'Art', 'Dance', 'Literature', 'Debate', 'Finance', 'Design', 'Gaming'];
  interestNames.forEach((name, idx) => db.interests.push({ id: idx + 1, name, created_at: timeStr }));

  for (let i = 1; i <= 30; i++) {
    db.user_interests.push({ id: i, user_id: (i % 20) + 1, interest_id: (i % 16) + 1, created_at: timeStr });
  }

  const clubCategories = ['Games', 'Technical', 'Cultural', 'Sports', 'Science', 'Arts', 'Literature'];
  for (let i = 1; i <= 15; i++) {
    const uniId = (i % 2) + 1;
    
    db.clubs.push({ 
      id: i, 
      name: `Club ${i}`, 
      slug: `club-${i}`, 
      category: clubCategories[i % clubCategories.length], 
      description: `Description for Club ${i}`, 
      objectives: `Objectives of Club ${i}`,
      logo_url: `/logos/club${i}.png`,
      banner: 'robotics',
      status: 'active', 
      faculty_advisor_id: 4, 
      member_count_cache: 10 + i,
      university_id: uniId 
    });
    
    db.club_interests.push({ id: i, club_id: i, interest_id: (i % 16) + 1, created_at: timeStr });
    
    db.club_memberships.push({ 
      id: i, 
      user_id: (i % 20) + 1, 
      club_id: i, 
      role_in_club: i % 3 === 0 ? 'president' : 'member', 
      status: 'approved',
      applied_at: timeStr,
      decided_at: timeStr,
      approved_by: 4,
      rejection_reason: null
    });
    
    db.committees.push({ id: i, club_id: i, name: `Committee ${i}`, description: `Desc ${i}`, created_at: timeStr });
    
    db.committee_memberships.push({ id: i, committee_id: i, membership_id: i, joined_at: timeStr });
    
    db.announcements.push({ 
      id: i, 
      club_id: i, 
      posted_by: 1,
      title: `Announcement ${i}`, 
      body: `Content ${i}`, 
      target_audience: 'ALL_STUDENTS',
      created_at: timeStr 
    });
    
    db.budgets.push({ 
      id: i, 
      club_id: i, 
      title: 'Annual Budget',
      period_start: '2025-01-01', 
      period_end: '2025-12-31', 
      allocated_amount: 50000 + i*1000, 
      status: 'APPROVED', 
      created_by: 1,
      created_at: timeStr 
    });
  }

  db.club_creation_requests.push({ 
    id: 1, 
    proposed_name: "Astronomy Club", 
    proposed_category: "Science", 
    proposal_description: "Stargazing and astrophotography",
    requested_by: 1, 
    status: "PENDING", 
    reviewed_by: null,
    review_comments: null,
    resulting_club_id: null,
    created_at: timeStr,
    decided_at: null
  });

  const eventTemplates = [
    {title: "Inter-College Chess Championship", desc: "Open chess tournament.", banner: "sports", is_public: true, capacity: 64, interests: [7]},
    {title: "Robo Sumo WAR", desc: "Build. Battle. Dominate.", banner: "robotics", is_public: true, capacity: 100, interests: [2, 8]},
    {title: "Musical Night", desc: "Live music performances by various bands.", banner: "music", is_public: true, capacity: 500, interests: [4, 9]},
    {title: "Web3 Workshop BootCamp", desc: "Learn the basics of decentralized web.", banner: "tech", is_public: false, capacity: 40, interests: [8]},
    {title: "Hackathon 2026", desc: "48-hour coding marathon.", banner: "coding", is_public: true, capacity: 200, interests: [6, 8]},
    {title: "AI Seminar", desc: "Guest lecture on AI.", banner: "tech", is_public: false, capacity: 80, interests: [1]}
  ];

  let eventInterestId = 1;
  for (let i = 1; i <= 50; i++) {
    const template = eventTemplates[i % eventTemplates.length];
    const daysOffset = Math.floor(Math.random() * 40) - 15; 
    const startDate = new Date(now.getTime() + daysOffset * 24 * 60 * 60 * 1000);
    const endDate = new Date(startDate.getTime() + (Math.floor(Math.random() * 4) + 2) * 60 * 60 * 1000);
    const regDeadline = new Date(startDate.getTime() - 2 * 24 * 60 * 60 * 1000);
    
    let status = "SCHEDULED";
    if (now > endDate) status = "COMPLETED";
    else if (now >= startDate && now <= endDate) status = "ONGOING";
    
    db.events.push({
      id: i,
      club_id: (i % 15) + 1,
      title: `${template.title} ${i}`,
      description: template.desc,
      venue: ["Main Auditorium", "LA 2-204", "Sports Complex", "Seminar Hall", "SAC"][Math.floor(Math.random() * 5)],
      start_at: startDate.toISOString().slice(0, 19).replace('T', ' '),
      end_at: endDate.toISOString().slice(0, 19).replace('T', ' '),
      registration_deadline: regDeadline.toISOString().slice(0, 19).replace('T', ' '),
      capacity: template.capacity,
      status: status,
      banner: template.banner,
      created_by: 4,
      requires_external_participants: template.is_public,
      is_public: template.is_public
    });

    for (const intId of template.interests) {
      db.event_interests.push({ id: eventInterestId++, event_id: i, interest_id: intId, created_at: timeStr });
    }

    db.event_sessions.push({ 
      id: i, 
      event_id: i, 
      title: `Session ${i}`, 
      description: 'Session overview',
      venue: 'Room 101',
      start_at: startDate.toISOString().slice(0, 19).replace('T', ' '), 
      end_at: endDate.toISOString().slice(0, 19).replace('T', ' '), 
      session_order: 1,
      created_at: timeStr
    });
    
    db.event_registrations.push({ 
      id: i, 
      event_id: i, 
      user_id: (i % 20) + 1, 
      registered_at: timeStr,
      status: 'CONFIRMED',
      qr_code_token: `QR_TOKEN_${i}`
    });
    
    db.attendance_records.push({ 
      id: i, 
      event_id: i, 
      user_id: (i % 20) + 1, 
      checked_in_at: startDate.toISOString().slice(0, 19).replace('T', ' '), 
      recorded_by: 4 
    });
    
    db.volunteer_assignments.push({ 
      id: i, 
      event_id: i, 
      assignee_membership_id: (i % 15) + 1,
      assigned_by: 1,
      task_description: 'Manage crowd',
      status: 'ASSIGNED',
      due_at: timeStr,
      created_at: timeStr 
    });
    
    db.expenses.push({ 
      id: i, 
      budget_id: (i % 15) + 1, 
      description: 'Event Supplies', 
      amount: 1000 + i*10, 
      category: 'SUPPLIES',
      receipt_document_id: null,
      submitted_by: 1, 
      status: 'APPROVED', 
      approval_status: 'APPROVED',
      approved_by: 4,
      approval_date: timeStr,
      approval_remarks: 'Approved by faculty',
      created_at: timeStr 
    });
  }

  for (let i = 1; i <= 10; i++) {
    db.external_participants.push({ 
      id: i, 
      event_id: (i % 50) + 1,
      user_id: null,
      full_name: `Guest ${i}`, 
      email: `guest${i}@org.com`, 
      affiliation: 'Org', 
      participant_type: 'GUEST_SPEAKER',
      registered_at: timeStr
    });
    
    db.documents.push({ 
      id: i, 
      owner_id: 4, 
      club_id: (i % 15) + 1,
      event_id: null,
      doc_type: 'GUIDELINES',
      file_url: `/docs/doc${i}.pdf`, 
      title: `Doc ${i}`,
      created_at: timeStr
    });
    
    db.notifications.push({ 
      id: i, 
      user_id: (i % 20) + 1,
      type: 'SYSTEM',
      title: 'Notice', 
      body: `Message ${i}`, 
      channel: 'IN_APP',
      is_read: false,
      sent_via_resend: false,
      related_entity_type: null,
      related_entity_id: null,
      created_at: timeStr
    });
    
    db.support_tickets.push({ 
      id: i, 
      raised_by: (i % 20) + 1, 
      club_id: null,
      title: 'Issue with app',
      description: `Desc ${i}`, 
      ticket_type: 'SUPPORT',
      priority: 'MEDIUM',
      status: 'OPEN', 
      assigned_agent_id: 5,
      is_offensive: false,
      resolution_rating: null,
      university_id: (i % 2) + 1,
      created_at: timeStr
    });
    
    db.ticket_responses.push({ 
      id: i, 
      ticket_id: i, 
      responder_id: 5, 
      body: 'We are looking into this',
      is_resolution: false,
      created_at: timeStr
    });
    
    db.emergency_reports.push({ 
      id: i, 
      reported_by: (i % 20) + 1, 
      event_id: (i % 50) + 1, 
      category: 'MEDICAL', 
      description: 'Minor injury', 
      status: 'RESOLVED',
      handled_by: 5,
      created_at: timeStr,
      resolved_at: timeStr
    });
    
    db.reward_points_ledger.push({ 
      id: i, 
      user_id: (i % 20) + 1, 
      points: 50, 
      reason: 'Volunteer Work',
      source_event_id: (i % 50) + 1,
      created_at: timeStr
    });
    
    db.reward_redemptions.push({ 
      id: i, 
      user_id: (i % 20) + 1, 
      points_spent: 50,
      reward_description: 'Food Voucher', 
      status: 'FULFILLED',
      approved_by: 4,
      created_at: timeStr
    });
    
    db.sponsors.push({ 
      id: i, 
      organization_name: `Sponsor ${i}`,
      contact_email: `sp${i}@tech.com`,
      contact_person: `Mr. SP ${i}`,
      created_at: timeStr 
    });
    
    db.club_sponsors.push({ 
      id: i, 
      club_id: (i % 15) + 1, 
      sponsor_id: i, 
      sponsorship_details: 'Providing $5000 in equipment' 
    });
    
    db.club_join_applications.push({ 
      id: i, 
      user_id: (i % 20) + 1, 
      club_id: (i % 15) + 1, 
      motivation: "Interested",
      contribution: "Skills",
      previous_experience: "None",
      skills: "Coding",
      portfolio_url: null,
      resume_document_id: null,
      weekly_availability: 10,
      status: 'PENDING', 
      reviewed_by: null,
      review_comments: null,
      applied_at: timeStr,
      reviewed_at: null
    });
    
    db.application_interests.push({ id: i, application_id: i, interest_id: (i % 16) + 1 });
  }

  // Audit Logs (CREATE, UPDATE, DELETE categories as requested)
  const auditActions = ['CREATE', 'UPDATE', 'DELETE'];
  for (let i = 1; i <= 30; i++) {
    const action = auditActions[i % auditActions.length];
    db.audit_logs.push({ 
      id: i, 
      user_id: (i % 5) + 1, 
      university_id: (i % 2) + 1,
      action: action, 
      entity_type: i % 2 === 0 ? 'Club' : 'Event', 
      entity_id: (i % 15) + 1, 
      details: `${action} operation performed` 
    });
  }

  const dbPath = path.join(__dirname, 'db.json');
  fs.writeFileSync(dbPath, JSON.stringify(db, null, 2));
  console.log("Generated 100% normalized db.json with all 33 tables successfully!");
};

generateDb();
