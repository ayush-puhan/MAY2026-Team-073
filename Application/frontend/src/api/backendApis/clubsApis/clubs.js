import { api } from '../../api';

export const clubsApi = {
  getAllClubs: async (universityId = null) => {
    const endpoint = universityId ? `/clubs?university_id=${universityId}` : '/clubs';
    const res = await api.get(endpoint);
    return res.data;
  },

  getClubById: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}`);
    return res.data;
  },

  getUserClubs: async (userId) => {
    const res = await api.get(`/users/${userId}/clubs`);
    return res.data;
  },

  getUserRoleInClub: async (userId, clubId) => {
    const res = await api.get(`/clubs/${clubId}/members/${userId}/role`);
    return res.data?.role_in_club || null;
  },

  getClubMembers: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/members`);
    return res.data;
  },

  getMembershipRequests: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/membership-requests`);
    return res.data;
  },

  joinClub: async (clubId, userId, role = 'member', reason = '') => {
    const res = await api.post(`/clubs/${clubId}/join`, {
      role_in_club: role,
      reason: reason
    });
    return res.data;
  },

  approveMembership: async (membershipId, approvedBy) => {
    const res = await api.patch(`/api/memberships/${membershipId}/approve`);
    return res.data;
  },

  rejectMembership: async (membershipId, rejectedBy, reason = '') => {
    const res = await api.patch(`/api/memberships/${membershipId}/reject`, { reason });
    return res.data;
  },

  updateMemberRole: async (membershipId, newRole, changedBy) => {
    const res = await api.patch(`/api/memberships/${membershipId}/role`, { role: newRole });
    return res.data;
  },

  removeMember: async (membershipId, removedBy) => {
    const res = await api.delete(`/api/memberships/${membershipId}`);
    return res.data;
  },

  leaveClub: async (membershipId, userId) => {
    const res = await api.post(`/api/memberships/${membershipId}/leave`);
    return res.data;
  },

  // ── Volunteer Tasks ──

  getMyTasks: async (clubId, userId) => {
    const res = await api.get(`/api/clubs/${clubId}/tasks?user_id=${userId}`);
    return res.data;
  },

  getClubTasks: async (clubId) => {
    const res = await api.get(`/api/clubs/${clubId}/tasks`);
    return res.data;
  },

  createTask: async (eventId, assigneeMembershipId, assignedBy, description, dueAt) => {
    const res = await api.post('/api/volunteer-tasks', {
      event_id: eventId,
      assignee_membership_id: assigneeMembershipId,
      task_description: description,
      due_at: dueAt
    });
    return res.data;
  },

  updateTaskStatus: async (taskId, newStatus, userId) => {
    const res = await api.patch(`/api/volunteer-tasks/${taskId}/status`, { status: newStatus });
    return res.data;
  },

  checkOverdueTasks: async () => {
    const res = await api.post('/api/volunteer-tasks/check-overdue');
    return res.data;
  },

  // ── Announcements ──

  getClubAnnouncements: async (clubId) => {
    const res = await api.get(`/api/clubs/${clubId}/announcements`);
    return res.data;
  },

  // ── Club Settings ──

  updateClubSettings: async (clubId, updates, userId) => {
    const res = await api.patch(`/api/clubs/${clubId}/settings`, updates);
    return res.data;
  },

  // ── Club Applications (New Workflow) ──

  submitJoinApplication: async (clubId, userId, applicationData) => {
    const res = await api.post(`/api/clubs/${clubId}/applications`, { ...applicationData, user_id: userId });
    return res.data;
  },

  getClubApplications: async (clubId) => {
    const res = await api.get(`/api/clubs/${clubId}/applications`);
    return res.data;
  },

  reviewApplication: async (applicationId, decision, reviewerId, reviewComments = '') => {
    const res = await api.patch(`/api/club-applications/${applicationId}/review`, {
      decision,
      reviewer_id: reviewerId,
      review_comments: reviewComments
    });
    return res.data;
  },

  getUserApplications: async (userId) => {
    const res = await api.get(`/api/users/${userId}/club-applications`);
    return res.data;
  },

  // ── Club Interests ──

  getClubInterests: async (clubId) => {
    const res = await api.get(`/api/clubs/${clubId}/interests`);
    return res.data;
  },

  setClubInterests: async (clubId, interestIds) => {
    const res = await api.post(`/api/clubs/${clubId}/interests`, { interests: interestIds });
    return res.data;
  },

  // ── Club Creation Workflow (Phase 2) ──

  getClubCreationRequests: async () => {
    const res = await api.get('/api/club-creation-requests');
    return res.data;
  },

  getFacultyClubRequests: async (facultyAdvisorId) => {
    const res = await api.get(`/api/club-creation-requests?faculty_advisor_id=${facultyAdvisorId}`);
    return res.data;
  },

  requestClubCreation: async (requesterId, clubData) => {
    const res = await api.post('/api/club-creation-requests', {
      requester_id: requesterId,
      ...clubData
    });
    return res.data;
  },

  approveClubRequest: async (requestId, adminId) => {
    const res = await api.patch(`/api/club-creation-requests/${requestId}/approve`, { admin_id: adminId });
    return res.data;
  },

  rejectClubRequest: async (requestId, rejectorId) => {
    const res = await api.patch(`/api/club-creation-requests/${requestId}/reject`, { rejector_id: rejectorId });
    return res.data;
  },

  // ── Create Event ──

  createEvent: async (eventData) => {
    const res = await api.post('/api/events', eventData);
    return res.data;
  }
};
