export const USER_ROLE = {
  STUDENT: 'student',
  FACULTY_ADVISOR: 'faculty_advisor',
  STUDENT_AFFAIRS_OFFICE: 'student_affairs_office',
  DEAN_STUDENT_WELFARE: 'dean_student_welfare',
  SYSTEM_ADMIN: 'system_admin'
};

export const USER_ROLES_OPTIONS = [
  { value: USER_ROLE.STUDENT, label: 'Student' },
  { value: USER_ROLE.FACULTY_ADVISOR, label: 'Faculty Advisor' },
  { value: USER_ROLE.STUDENT_AFFAIRS_OFFICE, label: 'Student Affairs Office' },
  { value: USER_ROLE.DEAN_STUDENT_WELFARE, label: 'Dean of Student Welfare' },
  { value: USER_ROLE.SYSTEM_ADMIN, label: 'System Administrator' }
];

export const TICKET_STATUS = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  RESOLVED: 'Resolved',
  CLOSED: 'Closed'
};

export const TICKET_STATUS_OPTIONS = [
  { value: TICKET_STATUS.OPEN, label: 'Open' },
  { value: TICKET_STATUS.IN_PROGRESS, label: 'In Progress' },
  { value: TICKET_STATUS.RESOLVED, label: 'Resolved' },
  { value: TICKET_STATUS.CLOSED, label: 'Closed' }
];

export const TICKET_PRIORITY = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical'
};

export const TICKET_PRIORITY_OPTIONS = [
  { value: TICKET_PRIORITY.LOW, label: 'Low' },
  { value: TICKET_PRIORITY.MEDIUM, label: 'Medium' },
  { value: TICKET_PRIORITY.HIGH, label: 'High' },
  { value: TICKET_PRIORITY.CRITICAL, label: 'Critical' }
];

export const TICKET_TYPE = {
  SUPPORT: 'Support',
  BUG: 'Bug',
  FEATURE_REQUEST: 'Feature Request',
  INQUIRY: 'Inquiry'
};

export const TICKET_TYPE_OPTIONS = [
  { value: TICKET_TYPE.SUPPORT, label: 'Support' },
  { value: TICKET_TYPE.BUG, label: 'Bug' },
  { value: TICKET_TYPE.FEATURE_REQUEST, label: 'Feature Request' },
  { value: TICKET_TYPE.INQUIRY, label: 'Inquiry' }
];

export const EMERGENCY_CATEGORY = {
  HARASSMENT: 'harassment',
  MEDICAL: 'medical',
  WHEELCHAIR_ASSISTANCE: 'wheelchair_assistance',
  OTHER_EMERGENCY: 'other_emergency'
};

export const EMERGENCY_CATEGORY_OPTIONS = [
  { value: EMERGENCY_CATEGORY.HARASSMENT, label: 'Harassment' },
  { value: EMERGENCY_CATEGORY.MEDICAL, label: 'Medical Issue' },
  { value: EMERGENCY_CATEGORY.WHEELCHAIR_ASSISTANCE, label: 'Wheelchair Assistance' },
  { value: EMERGENCY_CATEGORY.OTHER_EMERGENCY, label: 'Other Emergency' }
];

export const EMERGENCY_STATUS = {
  REPORTED: 'reported',
  ACKNOWLEDGED: 'acknowledged',
  IN_PROGRESS: 'in_progress',
  RESOLVED: 'resolved'
};

export const EMERGENCY_STATUS_OPTIONS = [
  { value: EMERGENCY_STATUS.REPORTED, label: 'Reported' },
  { value: EMERGENCY_STATUS.ACKNOWLEDGED, label: 'Acknowledged' },
  { value: EMERGENCY_STATUS.IN_PROGRESS, label: 'In Progress' },
  { value: EMERGENCY_STATUS.RESOLVED, label: 'Resolved' }
];

// ── Club Member Roles ──
export const CLUB_MEMBER_ROLE = {
  APPLICANT: 'applicant',
  MEMBER: 'member',
  VOLUNTEER_COORDINATOR: 'volunteer_coordinator',
  EVENT_COORDINATOR: 'event_coordinator',
  SECRETARY: 'secretary',
  TREASURER: 'treasurer',
  VICE_PRESIDENT: 'vice_president',
  PRESIDENT: 'president'
};

export const CLUB_MEMBER_ROLE_OPTIONS = [
  { value: CLUB_MEMBER_ROLE.MEMBER, label: 'Member' },
  { value: CLUB_MEMBER_ROLE.VOLUNTEER_COORDINATOR, label: 'Volunteer Coordinator' },
  { value: CLUB_MEMBER_ROLE.EVENT_COORDINATOR, label: 'Event Coordinator' },
  { value: CLUB_MEMBER_ROLE.SECRETARY, label: 'Secretary' },
  { value: CLUB_MEMBER_ROLE.TREASURER, label: 'Treasurer' },
  { value: CLUB_MEMBER_ROLE.VICE_PRESIDENT, label: 'Vice President' },
  { value: CLUB_MEMBER_ROLE.PRESIDENT, label: 'President' }
];

// ── Membership Status ──
export const MEMBERSHIP_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  WITHDRAWN: 'withdrawn'
};

// ── Club Status ──
export const CLUB_STATUS = {
  PENDING: 'pending',
  ACTIVE: 'active',
  SUSPENDED: 'suspended',
  ARCHIVED: 'archived'
};

// ── Club Creation Request Status ──
export const CLUB_REQUEST_STATUS = {
  SUBMITTED: 'submitted',
  UNDER_REVIEW: 'under_review',
  APPROVED: 'approved',
  REJECTED: 'rejected'
};

// ── Event Status ──
export const EVENT_STATUS = {
  SCHEDULED: 'scheduled',
  ONGOING: 'ongoing',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
};

// ── Volunteer Task Status ──
export const VOLUNTEER_TASK_STATUS = {
  ASSIGNED: 'assigned',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  MISSED: 'missed'
};

// ── Budget Status ──
export const BUDGET_STATUS = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CLOSED: 'closed'
};

// ── Expense Status ──
export const EXPENSE_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  REIMBURSED: 'reimbursed'
};

// ── Notification ──
export const NOTIFICATION_TYPE = {
  MEMBERSHIP_UPDATE: 'membership_update',
  EVENT_REMINDER: 'event_reminder',
  BUDGET_APPROVAL: 'budget_approval',
  TICKET_UPDATE: 'ticket_update',
  PASSWORD_RESET: 'password_reset',
  CERTIFICATE_READY: 'certificate_ready',
  EMERGENCY_ALERT: 'emergency_alert',
  ANNOUNCEMENT: 'announcement'
};

export const NOTIFICATION_CHANNEL = {
  IN_APP: 'in_app',
  EMAIL: 'email',
  BOTH: 'both'
};

// ── Announcement Audience ──
export const ANNOUNCEMENT_AUDIENCE = {
  ALL_MEMBERS: 'all_members',
  COMMITTEE: 'committee',
  LEADERSHIP: 'leadership',
  SYSTEM_WIDE: 'system_wide',
  UNIVERSITY_WIDE: 'university_wide'
};

// ── Registration Status ──
export const REGISTRATION_STATUS = {
  REGISTERED: 'registered',
  WAITLISTED: 'waitlisted',
  CANCELLED: 'cancelled'
};

// ── Document Type ──
export const DOCUMENT_TYPE = {
  CERTIFICATE: 'certificate',
  RECEIPT: 'receipt',
  REPORT: 'report',
  GENERAL: 'general'
};

// ── External Participant Type ──
export const EXTERNAL_PARTICIPANT_TYPE = {
  OTHER_UNIVERSITY_STUDENT: 'other_university_student',
  GUEST_SPEAKER: 'guest_speaker',
  COMPETITION_PARTICIPANT: 'competition_participant'
};

// ── Redemption Status ──
export const REDEMPTION_STATUS = {
  REQUESTED: 'requested',
  APPROVED: 'approved',
  FULFILLED: 'fulfilled',
  REJECTED: 'rejected'
};

// ── Auth Provider ──
export const AUTH_PROVIDER = {
  LOCAL: 'local',
  GOOGLE: 'google'
};

// ── Gender ──
export const GENDER = {
  MALE: 'male',
  FEMALE: 'female',
  OTHER: 'other',
  PREFER_NOT_TO_SAY: 'prefer_not_to_say'
};
