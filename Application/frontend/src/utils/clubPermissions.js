/**
 * Centralized club role permission utility.
 * 
 * A single student can hold DIFFERENT roles across different clubs.
 * Always pass the role for the SPECIFIC club being viewed.
 * 
 * ── ROLE HIERARCHY (highest → lowest) ──
 * president > vice_president > treasurer > secretary >
 * event_coordinator > volunteer_coordinator > member > applicant
 */

import { dashboardIcons } from '../assets/icons/registry';

// ── Role hierarchy from highest to lowest ──
const ROLE_HIERARCHY = [
  'president',
  'vice_president',
  'treasurer',
  'secretary',
  'event_coordinator',
  'volunteer_coordinator',
  'member'
];

// All approved member roles (excludes applicant)
const APPROVED_ROLES = [...ROLE_HIERARCHY];

// ── Rank Helpers ──
export const getRoleRank = (role) => {
  const idx = ROLE_HIERARCHY.indexOf(role);
  return idx === -1 ? ROLE_HIERARCHY.length + 1 : idx; // applicant gets lowest
};

export const hasMinRole = (role, minRole) => {
  return getRoleRank(role) <= getRoleRank(minRole);
};

// ── Permission Checkers (Explicit Capabilities) ──

export const isApplicant = (role) => role === 'applicant';
export const isApprovedMember = (role) => APPROVED_ROLES.includes(role);

// GENERAL
export const canViewDashboard = (role) => isApprovedMember(role);
export const canViewMembers = (role) => isApprovedMember(role);
export const canViewCertificates = (role) => isApprovedMember(role);
export const canLeaveClub = (role) => isApprovedMember(role) && role !== 'president';
export const canWithdrawApplication = (role) => role === 'applicant';

// MEMBERSHIP
export const canManageMembers = (role) => ['president', 'vice_president', 'secretary'].includes(role);

// EVENTS
export const canViewEvents = (role) => isApprovedMember(role);
export const canCreateEvents = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator'].includes(role);
export const canManageEvents = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator'].includes(role);
export const canManageEventSessions = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator'].includes(role);
export const canApproveEvents = (role) => role === 'president';
export const canManageAttendance = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator'].includes(role);

// TASKS & VOLUNTEERS
export const canViewMyTasks = (role) => isApprovedMember(role);
export const canManageTasks = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator', 'volunteer_coordinator'].includes(role);
export const canManageVolunteers = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator', 'volunteer_coordinator'].includes(role);

// Strict hierarchy enforcement for task assignment: Assigner must be higher rank than Target
export const canAssignTaskTo = (assignerRole, targetRole) => getRoleRank(assignerRole) < getRoleRank(targetRole);

// RESOURCES
export const canManageResources = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator', 'volunteer_coordinator'].includes(role);

// COMMITTEES (Global Club Permissions)
export const canManageCommittees = (role) => ['president', 'vice_president'].includes(role);
export const canViewCommittees = (role) => isApprovedMember(role);

// ANNOUNCEMENTS
export const canViewAnnouncements = (role) => isApprovedMember(role);
export const canPostClubWideAnnouncement = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator'].includes(role);
export const canPostAnnouncement = (role) => canPostClubWideAnnouncement(role);

// FINANCE
export const canViewBudget = (role) => ['president', 'vice_president', 'treasurer', 'secretary'].includes(role);
export const canCreateExpense = (role) => ['president', 'treasurer'].includes(role);
export const canEditExpense = (role) => ['president', 'treasurer'].includes(role);
export const canDeleteExpense = (role) => ['president', 'treasurer'].includes(role);
export const canApproveExpenses = (role) => ['president', 'treasurer'].includes(role); 
export const canExportFinancials = (role) => ['president', 'treasurer'].includes(role);
export const canManageBudget = (role) => ['president', 'treasurer'].includes(role);

// ROLES
export const canAssignRoles = (role) => ['president', 'vice_president'].includes(role);
export const canAssignPresident = (role) => ['president'].includes(role);
export const canManageRoles = (role) => canAssignRoles(role);

// Strict hierarchy enforcement for role assignment
export const canAssignRoleTo = (assignerRole, targetCurrentRole, newRole) => {
  if (!canAssignRoles(assignerRole)) return false;
  
  const assignerRank = getRoleRank(assignerRole);
  const targetRank = getRoleRank(targetCurrentRole);
  const newRoleRank = getRoleRank(newRole);

  // 1. Assigner cannot modify someone who is strictly equal or higher in rank (except President can modify President for transfer, but that's a special action)
  if (assignerRank >= targetRank && assignerRole !== 'president') return false;

  // 2. Assigner cannot assign a role that is equal or higher than their own rank
  if (assignerRank >= newRoleRank && assignerRole !== 'president') return false;

  return true;
};

// SETTINGS
export const canViewClubSettings = (role) => ['president', 'vice_president'].includes(role);
export const canEditClubSettings = (role) => ['president'].includes(role);

// ANALYTICS
export const canViewPersonalAnalytics = (role) => isApprovedMember(role);
export const canViewCommitteeAnalytics = (role) => ['president', 'vice_president'].includes(role);
export const canViewVolunteerAnalytics = (role) => ['president', 'vice_president', 'volunteer_coordinator'].includes(role);
export const canViewEventAnalytics = (role) => ['president', 'vice_president', 'event_coordinator'].includes(role);
export const canViewFinanceAnalytics = (role) => ['president', 'treasurer'].includes(role);
export const canViewClubAnalytics = (role) => ['president', 'vice_president', 'secretary'].includes(role);
export const canViewCompleteAnalytics = (role) => ['president'].includes(role);
export const canViewAnalytics = (role) => ['president', 'vice_president', 'treasurer', 'secretary', 'event_coordinator', 'volunteer_coordinator'].includes(role);

// ── Committee Scoped Permissions ──
export const hasCommitteePermission = (action, committeeRole) => {
  const normalizedRole = (committeeRole || '').toLowerCase();
  
  switch (action) {
    case 'view_committee':
    case 'view_members':
      return ['head', 'co_head', 'member'].includes(normalizedRole);
    
    case 'view_tasks':
    case 'update_tasks':
    case 'upload_resources':
      return ['head', 'co_head', 'member'].includes(normalizedRole);

    case 'create_announcements':
    case 'manage_members':
    case 'assign_tasks':
      return ['head', 'co_head'].includes(normalizedRole);

    case 'manage_club':
      return false; // Committee members never have club-wide authority by default
      
    default:
      return false;
  }
};


// ── Display Helpers ──

export const getRoleLabel = (role) => {
  const labels = {
    president: 'President',
    vice_president: 'Vice President',
    treasurer: 'Treasurer',
    secretary: 'Secretary',
    event_coordinator: 'Event Coordinator',
    volunteer_coordinator: 'Volunteer Coordinator',
    member: 'Member',
    applicant: 'Applicant'
  };
  return labels[role] || role;
};

export const getRoleIcon = (role) => {
  const icons = {
    president: 'mdi:crown-outline',
    vice_president: 'mdi:shield-star-outline',
    treasurer: 'mdi:cash-multiple',
    secretary: 'mdi:file-document-edit-outline',
    event_coordinator: 'mdi:calendar-star',
    volunteer_coordinator: 'mdi:hand-heart-outline',
    member: 'mdi:account-outline',
    applicant: 'mdi:account-clock-outline'
  };
  return icons[role] || 'mdi:account-outline';
};

export const getRoleColor = (role) => {
  const colors = {
    president: 'var(--gold)',
    vice_president: 'var(--primary)',
    treasurer: '#10b981',
    secretary: '#8b5cf6',
    event_coordinator: '#f59e0b',
    volunteer_coordinator: '#06b6d4',
    member: 'var(--muted-foreground)',
    applicant: '#94a3b8'
  };
  return colors[role] || 'var(--muted-foreground)';
};

export const getRoleDescription = (role) => {
  const descriptions = {
    president: 'Full control: settings, roles, budgets, analytics, events, tasks, members.',
    vice_president: 'Leadership: manage members, events, tasks, committees, budgets, analytics.',
    treasurer: 'Finance: manage budgets, submit expenses, view analytics. Plus standard member access.',
    secretary: 'Communication: manage membership requests, post announcements. Plus standard member access.',
    event_coordinator: 'Events: create and manage club events, handle attendance. Plus standard member access.',
    volunteer_coordinator: 'Tasks: create, assign, and track volunteer tasks. Plus standard member access.',
    member: 'View dashboard, events, tasks, members. Earn certificates.',
    applicant: 'Application pending review. You can view status or withdraw.'
  };
  return descriptions[role] || '';
};

// ── Context Panel Builder ──
export const getClubPanelSections = (role, basePath, pendingRequestsCount = 0) => {
  const sections = [];

  if (isApplicant(role)) {
    sections.push({
      title: 'APPLICATION',
      items: [
        { to: `${basePath}/application-status`, icon: 'mdi:progress-clock', label: 'Application Status' },
        { to: `${basePath}/withdraw`, icon: 'mdi:close-circle-outline', label: 'Withdraw Application' }
      ]
    });
    return sections;
  }

  const overviewItems = [
    { to: `${basePath}/dashboard`, icon: 'mdi:view-dashboard-outline', label: 'Dashboard' }
  ];
  if (canViewAnnouncements(role)) {
    overviewItems.push({ to: `${basePath}/announcements`, icon: dashboardIcons.announcements, label: 'Announcements' });
  }
  if (canViewAnalytics(role)) {
    overviewItems.push({ to: `${basePath}/analytics`, icon: 'mdi:chart-line', label: 'Analytics' });
  }
  sections.push({ title: 'OVERVIEW', items: overviewItems });

  if (canManageMembers(role) || canAssignRoles(role)) {
    const memberItems = [
      { to: `${basePath}/members`, icon: 'mdi:account-group-outline', label: 'Members Directory' }
    ];
    if (canManageMembers(role)) {
      memberItems.push({ 
        to: `${basePath}/requests`, 
        icon: 'mdi:account-clock-outline', 
        label: 'Membership Requests',
        badge: pendingRequestsCount > 0 ? pendingRequestsCount : null
      });
    }
    if (canAssignRoles(role)) {
      memberItems.push({ to: `${basePath}/roles`, icon: 'mdi:shield-account-outline', label: 'Manage Roles' });
    }
    sections.push({ title: 'MEMBERS', items: memberItems });
  }

  const eventItems = [];
  
  if (!canManageMembers(role) && !canAssignRoles(role)) {
    eventItems.push({ to: `${basePath}/members`, icon: 'mdi:account-group-outline', label: 'Members Directory' });
  }

  eventItems.push({ to: `${basePath}/events`, icon: 'mdi:calendar-outline', label: 'Club Events' });
  eventItems.push({ to: `${basePath}/tasks`, icon: 'mdi:clipboard-check-outline', label: 'My Tasks' });

  if (canManageTasks(role)) {
    eventItems.push({ to: `${basePath}/manage-tasks`, icon: 'mdi:clipboard-list-outline', label: 'Manage Tasks' });
  }

  sections.push({ title: 'EVENTS & TASKS', items: eventItems });

  const orgItems = [];
  if (canViewCommittees(role)) {
    orgItems.push({ to: `${basePath}/committees`, icon: 'mdi:account-multiple-outline', label: 'Committees' });
  }
  if (canManageResources(role) || isApprovedMember(role)) { // Everyone can view resources, managers can edit
    orgItems.push({ to: `${basePath}/resources`, icon: 'mdi:folder-outline', label: 'Resources' });
  }
  if (canViewBudget(role)) {
    orgItems.push({ to: `${basePath}/budget`, icon: 'mdi:wallet-outline', label: 'Budget & Finance' });
  }
  // Activity Log nav hidden for now
  // if (canManageCommittees(role)) {
  //   orgItems.push({ to: `${basePath}/activity-log`, icon: 'mdi:history', label: 'Activity Log' });
  // }
  if (canViewClubSettings(role)) {
    orgItems.push({ to: `${basePath}/settings`, icon: 'mdi:cog-outline', label: 'Club Settings' });
  }
  if (orgItems.length > 0) {
    sections.push({ title: 'ORGANIZATION', items: orgItems });
  }

  const personalItems = [
    { to: `${basePath}/certificates`, icon: 'mdi:certificate-outline', label: 'My Certificates' }
  ];
  if (canLeaveClub(role)) {
    personalItems.push({ to: `${basePath}/leave`, icon: 'mdi:logout-variant', label: 'Leave Club' });
  }
  sections.push({ title: 'PERSONAL', items: personalItems });

  return sections;
};
