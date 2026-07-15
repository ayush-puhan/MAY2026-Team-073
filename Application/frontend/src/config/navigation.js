// ══════════════════════════════════════════════════
// ClubConnect — Navigation Config
// ══════════════════════════════════════════════════
// Single source of truth for all sidebar navigation links.
// Nav items are resolved at runtime based on system role + club role.

import { dashboardIcons } from '../assets/icons/registry';
import { checkIsVerified } from '../utils/verification';

// ── Club Role Hierarchy (index = rank, higher = more permissions) ──
export const CLUB_ROLES = [
  'Student',              // 0 — no club membership
  'Club Member',          // 1
  'Committee Member',     // 2
  'Volunteer Coordinator',// 3
  'Event Coordinator',    // 4
  'Secretary',            // 5
  'Treasurer',            // 6
  'Vice President',       // 7
  'President',            // 8
];

// ── Base Student Nav (Platform Level) ──
export const STUDENT_NAV = [
  { name: 'Home',           path: '/student-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Discover Clubs', path: '/student-dashboard/discover', icon: dashboardIcons.discover },
  { name: 'My Clubs',       path: '/student-dashboard/my-clubs', icon: dashboardIcons.myClubs },
  { name: 'Events',         path: '/student-dashboard/events', icon: dashboardIcons.events },
  { name: 'Calendar',       path: '/student-dashboard/calendar', icon: 'mdi:calendar-outline' },
  { name: 'Rewards',        path: '/student-dashboard/rewards', icon: 'mdi:trophy-outline' },
  { name: 'AI Assistant',   path: '/student-dashboard/ai', icon: 'mdi:robot-outline' },
  { name: 'Helpdesk',       path: '/student-dashboard/helpdesk', icon: 'mdi:lifebuoy' },
];

// ── System Admin Nav ──
export const ADMIN_NAV = [
  { name: 'Dashboard',           path: '/admin-dashboard',          icon: dashboardIcons.dashboard },
  { name: 'User Management',     path: '/admin-dashboard/users',    icon: dashboardIcons.userMgmt },
  { name: 'Role Directory', path: '/admin-dashboard/roles',    icon: dashboardIcons.rolesMgmt },
  { name: 'Reports & Analytics', path: '/admin-dashboard/reports',  icon: dashboardIcons.reports },
  { name: 'Platform Settings',   path: '/admin-dashboard/settings', icon: dashboardIcons.settings },
  { name: 'Support Management',  path: '/admin-dashboard/support',  icon: dashboardIcons.supportMgmt },
  { name: 'Audit & Activity',    path: '/admin-dashboard/audit',    icon: dashboardIcons.auditLogs },
];

// ── University Admin Nav (Dean, SAO) ──
export const UNIVERSITY_ADMIN_NAV = [
  { name: 'Dashboard',        path: '/university-admin-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Club Approvals',   path: '/university-admin-dashboard/approvals', icon: dashboardIcons.clubApprovals },
  { name: 'Student Reports',  path: '/university-admin-dashboard/reports', icon: dashboardIcons.studentReports },
  { name: 'Events',           path: '/university-admin-dashboard/events', icon: dashboardIcons.eventMgmt },
  { name: 'Support Management', path: '/university-admin-dashboard/support', icon: dashboardIcons.supportMgmt },
  { name: 'Settings',         path: '/university-admin-dashboard/settings', icon: dashboardIcons.settings },
];

// ── Faculty Advisor Nav ──
export const FACULTY_ADVISOR_NAV = [
  { name: 'Dashboard',        path: '/faculty-advisor-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Advised Clubs',    path: '/faculty-advisor-dashboard/clubs', icon: dashboardIcons.advisedClubs },
  { name: 'Event Approvals',  path: '/faculty-advisor-dashboard/events', icon: dashboardIcons.eventApprovals },
  { name: 'Student Reports',  path: '/faculty-advisor-dashboard/reports', icon: dashboardIcons.studentReports },
  { name: 'Messages',         path: '/faculty-advisor-dashboard/messages', icon: dashboardIcons.messages },
  { name: 'Settings',         path: '/faculty-advisor-dashboard/settings', icon: dashboardIcons.settings },
];

const UNVERIFIED_NAV = [
  { name: 'Home',           path: '/student-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Events',         path: '/student-dashboard/events', icon: dashboardIcons.events },
  { name: 'Calendar',       path: '/student-dashboard/calendar', icon: 'mdi:calendar-outline' },
  { name: 'Helpdesk',       path: '/student-dashboard/helpdesk', icon: 'mdi:lifebuoy' },
];

/**
 * Build the final primary nav for a user based on their system role.
 * (Club-specific navigation is handled separately inside Club Workspaces).
 * 
 * @param {Object} user User object containing role and profile details
 * @returns {Array} Final nav link array
 */
export const getNavForUser = (user) => {
  const systemRole = typeof user === 'string' ? user : user?.role;
  const isVerified = checkIsVerified(user);
  
  switch (systemRole?.toLowerCase()) {
    case 'system_admin':
      return isVerified ? ADMIN_NAV : UNVERIFIED_NAV;
    case 'student_affairs_office':
    case 'dean_student_welfare':
      return isVerified ? UNIVERSITY_ADMIN_NAV : UNVERIFIED_NAV;
    case 'faculty_advisor':
      return isVerified ? FACULTY_ADVISOR_NAV : UNVERIFIED_NAV;
    case 'student':
    default:
      return isVerified ? STUDENT_NAV : UNVERIFIED_NAV;
  }
};

