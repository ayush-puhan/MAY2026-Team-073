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
