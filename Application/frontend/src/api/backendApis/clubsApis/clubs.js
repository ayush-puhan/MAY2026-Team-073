import { api } from '../../api';

export const clubsApi = {
  getAllClubs: async (universityId = null) => {
    const endpoint = universityId ? `/clubs?university_id=${universityId}` : '/clubs';
    const res = await api.get(endpoint);
    return res;
  },

  getClubById: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}`);
    return res;
  },
  getClubEvents: async (clubId) => {
    const response = await api.get(
        `/events?club_id=${clubId}`
    );
    
    return response;
  },
  getClubRecentActivity: async (clubId) => {
    return [];
  },
  getClubCommittees: async (clubId) => {
    const committees = await api.get(`/clubs/${clubId}/committees`);
    return committees;
  },
  getUserCertificates: async (userId) => {
    return await api.get(`/users/${userId}/certificates`);
  },
  getCommitteeMembers: async (committeeId) => {
    const members = await api.get(`/committees/${committeeId}/members`);
  return members;
  },
  getUserClubs: async (userId) => {
    const res = await api.get(`/users/${userId}/clubs`);
    return res;
  },

  getUserRoleInClub: async (userId, clubId) => {
    const res = await api.get(`/clubs/${clubId}/members/${userId}/role`);
    return res?.role_in_club || null;
  },

  getClubMembers: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/members`);
    return res;
  },

  getMembershipRequests: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/membership-requests`);
    return res;
  },

  joinClub: async (clubId, userId, role = 'member', reason = '') => {
    const res = await api.post(`/clubs/${clubId}/join`, {
      role_in_club: role,
      reason: reason
    });
    return res;
  },

  approveMembership: async (membershipId, approvedBy) => {
    const res = await api.patch(`/memberships/${membershipId}/approve`);
    return res;
  },

  rejectMembership: async (membershipId, rejectedBy, reason = '') => {
    const res = await api.patch(`/memberships/${membershipId}/reject`, { reason });
    return res;
  },

  updateMemberRole: async (membershipId, newRole, changedBy) => {
    const res = await api.patch(`/memberships/${membershipId}/role`, { role: newRole });
    return res;
  },

  removeMember: async (membershipId, removedBy) => {
    const res = await api.delete(`/memberships/${membershipId}`);
    return res;
  },

  leaveClub: async (membershipId, userId) => {
    const res = await api.post(`/memberships/${membershipId}/leave`);
    return res;
  },

  // ── Volunteer Tasks ──

  getMyTasks: async (clubId, userId) => {
    const res = await api.get(`/clubs/${clubId}/tasks?user_id=${userId}`);
    return res;
  },

  getClubTasks: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/tasks`);
    return res;
  },

  createTask: async (eventId, assigneeMembershipId, assignedBy, description, dueAt) => {
    const res = await api.post('/volunteer-tasks', {
      event_id: eventId,
      assignee_membership_id: assigneeMembershipId,
      task_description: description,
      due_at: dueAt
    });
    return res;
  },

  updateTaskStatus: async (taskId, newStatus, userId) => {
    const res = await api.patch(`/volunteer-tasks/${taskId}/status`, { status: newStatus });
    return res;
  },

  checkOverdueTasks: async () => {
    const res = await api.post('/volunteer-tasks/check-overdue');
    return res;
  },

  // ── Announcements ──

  getClubAnnouncements: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/announcements`);
    return res;
  },

  // ── Club Settings ──

  updateClubSettings: async (clubId, updates, userId) => {
    const res = await api.patch(`/clubs/${clubId}/settings`, updates);
    return res;
  },

  // ── Club Applications (New Workflow) ──

  submitJoinApplication: async (clubId, userId, applicationData) => {
    const res = await api.post(`/clubs/${clubId}/applications`, { ...applicationData, user_id: userId });
    return res;
  },

  getClubApplications: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/applications`);
    return res;
  },

  reviewApplication: async (applicationId, decision, reviewerId, reviewComments = '') => {
    const res = await api.patch(`/club-applications/${applicationId}/review`, {
      decision,
      reviewer_id: reviewerId,
      review_comments: reviewComments
    });
    return res;
  },

  getUserApplications: async (userId) => {
    const res = await api.get(`/users/${userId}/club-applications`);
    return res;
  },

  // ── Club Interests ──

  getClubInterests: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/interests`);
    return res;
  },

  setClubInterests: async (clubId, interestIds) => {
    const res = await api.post(`/clubs/${clubId}/interests`, { interests: interestIds });
    return res;
  },

  // ── Club Creation Workflow (Phase 2) ──

  getClubCreationRequests: async () => {
    const res = await api.get('/club-creation-requests');
    return res;
  },

  getFacultyClubRequests: async (facultyAdvisorId) => {
    const res = await api.get(`/club-creation-requests?faculty_advisor_id=${facultyAdvisorId}`);
    return res;
  },

  requestClubCreation: async (requesterId, clubData) => {
    const res = await api.post('/club-creation-requests', {
      requester_id: requesterId,
      ...clubData
    });
    return res;
  },

  approveClubRequest: async (requestId, adminId) => {
    const res = await api.patch(`/club-creation-requests/${requestId}/approve`, { admin_id: adminId });
    return res;
  },

  rejectClubRequest: async (requestId, rejectorId) => {
    const res = await api.patch(`/club-creation-requests/${requestId}/reject`, { rejector_id: rejectorId });
    return res;
  },

  // ── Create Event ──

  createEvent: async (eventData) => {
    const res = await api.post('/events', eventData);
    return res;
  }
};
