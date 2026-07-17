import { api } from '../../api';

export const universityAdminApi = {
  getStats: async () => api.get('/university-admin/stats'),
  getClubCreationRequests: async (status) => api.get(`/university-admin/club-requests${status ? `?status=${status}` : ''}`),
  decideClubCreationRequest: async (id, decision) => api.patch(`/university-admin/club-requests/${id}/decision`, decision),
  getPendingClubActivations: async () => api.get('/university-admin/clubs/pending-activation'),
  activateClub: async (clubId, facultyAdvisorId) => api.patch(`/university-admin/clubs/${clubId}/activate`, { faculty_advisor_id: facultyAdvisorId }),
  getFacultyAdvisors: async () => api.get('/university-admin/faculty-advisors'),
  getAllClubs: async () => api.get('/university-admin/clubs'),
  getAllEvents: async () => api.get('/university-admin/events'),
  getAnalytics: async () => api.get('/university-admin/analytics'),
  getAnnouncements: async () => api.get('/university-admin/announcements'),
  postAnnouncement: async (data) => api.post('/university-admin/announcements', data),
};
