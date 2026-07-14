// ══════════════════════════════════════════════════
// ClubConnect — Navigation Config
// ══════════════════════════════════════════════════
// Single source of truth for all sidebar navigation links.
// Nav items are resolved at runtime based on system role + club role.

import { dashboardIcons } from '../assets/icons/registry';

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
  { name: 'Dashboard',        path: '/admin-dashboard',        icon: dashboardIcons.dashboard },
  { name: 'Club Approvals',   path: '/admin-dashboard/approvals', icon: dashboardIcons.clubApprovals },
  { name: 'User Management',  path: '/admin-dashboard/users',     icon: dashboardIcons.userMgmt },
  { name: 'Reports',          path: '/admin-dashboard/reports',   icon: dashboardIcons.reports },
  { name: 'System Logs',      path: '/admin-dashboard/logs',      icon: dashboardIcons.systemLogs },
  { name: 'Settings',         path: '/admin-dashboard/settings',  icon: dashboardIcons.settings },
];

// ── University Admin Nav (Dean, SAO) ──
export const UNIVERSITY_ADMIN_NAV = [
  { name: 'Dashboard',        path: '/university-admin-dashboard', icon: dashboardIcons.dashboard },
  { name: 'Club Approvals',   path: '/university-admin-dashboard/approvals', icon: dashboardIcons.clubApprovals },
  { name: 'Student Reports',  path: '/university-admin-dashboard/reports', icon: dashboardIcons.studentReports },
  { name: 'Events',           path: '/university-admin-dashboard/events', icon: dashboardIcons.eventMgmt },
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


/**
 * Build the final primary nav for a user based on their system role.
 * (Club-specific navigation is handled separately inside Club Workspaces).
 * 
 * @param {'Student'|'Admin'|'University Admin'|'Faculty Advisor'|'student_affairs_office'|'dean_student_welfare'|'system_admin'} systemRole
 * @returns {Array} Final nav link array
 */
export const getNavForUser = (systemRole) => {
  switch (systemRole?.toLowerCase()) {
    case 'admin':
    case 'system_admin':
      return ADMIN_NAV;
    case 'university admin':
    case 'student_affairs_office':
    case 'dean_student_welfare':
      return UNIVERSITY_ADMIN_NAV;
    case 'faculty advisor':
    case 'faculty_advisor':
      return FACULTY_ADVISOR_NAV;
    case 'student':
    default:
      return STUDENT_NAV;
  }
};
