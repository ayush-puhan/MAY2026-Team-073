import { dashboardIcons } from '../assets/icons/registry';
import { checkIsVerified } from '../utils/verification';

// "?"? Club Role Hierarchy (index = rank, higher = more permissions) "?"?
export const CLUB_ROLES = [
  'Student',              // 0
  'Club Member',          // 1
  'Committee Member',     // 2
  'Volunteer Coordinator',// 3
  'Event Coordinator',    // 4
  'Secretary',            // 5
  'Treasurer',            // 6
  'Vice President',       // 7
  'President',            // 8
];

const getGlobalBottomNav = (basePath) => [
  { name: 'Calendar', path: `${basePath}/calendar`, icon: dashboardIcons.calendar },
  { name: 'Announcements', path: `${basePath}/announcements`, icon: dashboardIcons.announcements },
  { name: 'Helpdesk', path: `${basePath}/helpdesk`, icon: dashboardIcons.helpdesk }
];

export const STUDENT_NAV = [
  { name: 'Campus Home', path: '/student-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Clubs',       path: '/student-dashboard/clubs', icon: dashboardIcons.discover },
  { name: 'Events',      path: '/student-dashboard/events', icon: dashboardIcons.events },
  { name: 'Rewards',     path: '/student-dashboard/rewards', icon: dashboardIcons.rewards },
  { name: 'AI Assistant', path: '/student-dashboard/ai', icon: dashboardIcons.aiAssistant },
  ...getGlobalBottomNav('/student-dashboard')
];

export const ADMIN_NAV = [
  { name: 'Dashboard', path: '/admin-dashboard', icon: dashboardIcons.dashboard },
  { name: 'User Management',     path: '/admin-dashboard/users',    icon: dashboardIcons.userMgmt },
  { name: 'Role Directory',      path: '/admin-dashboard/roles',    icon: dashboardIcons.rolesMgmt },
  { name: 'Reports & Analytics', path: '/admin-dashboard/reports',  icon: dashboardIcons.reports },
  { name: 'Calendar', path: '/admin-dashboard/calendar', icon: dashboardIcons.calendar },
  { name: 'Announcements', path: '/admin-dashboard/announcements', icon: dashboardIcons.announcements },
  { name: 'Support Management',  path: '/admin-dashboard/support',  icon: dashboardIcons.helpdesk },
  { name: 'University Management', path: '/admin-dashboard/settings', icon: dashboardIcons.settings },
  // { name: 'Audit & Activity',    path: '/admin-dashboard/audit',    icon: dashboardIcons.auditLogs },
  { name: 'AI Assistant', path: '/admin-dashboard/ai', icon: dashboardIcons.aiAssistant }
];

export const UNIVERSITY_ADMIN_NAV = [
  { name: 'Dashboard', path: '/university-admin-dashboard', icon: dashboardIcons.dashboard },
  { name: 'All Clubs',        path: '/university-admin-dashboard/clubs', icon: dashboardIcons.accountGroupOutline },
  { name: 'Events',           path: '/university-admin-dashboard/events', icon: dashboardIcons.eventMgmt },
  { name: 'Club Approvals',   path: '/university-admin-dashboard/approvals', icon: dashboardIcons.clubApprovals },
  { name: 'Student Reports',  path: '/university-admin-dashboard/reports', icon: dashboardIcons.studentReports },
  
  { name: 'Emergency Reports', path: '/university-admin-dashboard/emergencies', icon: dashboardIcons.emergencyAlert },
  { name: 'AI Assistant', path: '/university-admin-dashboard/ai', icon: dashboardIcons.aiAssistant },
  ...getGlobalBottomNav('/university-admin-dashboard')
];

export const FACULTY_ADVISOR_NAV = [
  { name: 'Dashboard', path: '/faculty-advisor-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Advised Clubs',    path: '/faculty-advisor-dashboard/clubs', icon: dashboardIcons.advisedClubs },
  { name: 'Event Approvals',  path: '/faculty-advisor-dashboard/events', icon: dashboardIcons.eventApprovals },
  { name: 'Expense Approvals',  path: '/faculty-advisor-dashboard/reports', icon: dashboardIcons.studentReports },
  { name: 'AI Assistant', path: '/faculty-advisor-dashboard/ai', icon: dashboardIcons.aiAssistant },
  ...getGlobalBottomNav('/faculty-advisor-dashboard')
];

const UNVERIFIED_NAV = [
  { name: 'Campus Home', path: '/student-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Events',      path: '/student-dashboard/events', icon: dashboardIcons.events },
  { name: 'Rewards',     path: '/student-dashboard/rewards', icon: dashboardIcons.rewards },
  ...getGlobalBottomNav('/student-dashboard')
];

/**
 * Build the final primary nav for a user based on their system role.
 */
export const getNavForUser = (user) => {
  const systemRole = typeof user === 'string' ? user : user?.role;
  const isVerified = checkIsVerified(user);
  
  switch (systemRole?.toLowerCase()) {
    case 'system_admin':
      return ADMIN_NAV;
    case 'student_affairs_office':
    case 'dean_student_welfare':
      return UNIVERSITY_ADMIN_NAV;
    case 'faculty_advisor':
      return FACULTY_ADVISOR_NAV;
    case 'student':
    default:
      return isVerified ? STUDENT_NAV : UNVERIFIED_NAV;
  }
};


