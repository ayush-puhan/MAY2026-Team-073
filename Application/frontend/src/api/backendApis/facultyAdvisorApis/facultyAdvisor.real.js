import { api } from '../../api';

export const facultyAdvisorRealApi = {
  getStats: async (userId) => api.get(`/faculty/${userId}/stats`),
  getAdvisedClubs: async (userId) => api.get(`/faculty/${userId}/clubs`),
  getClubDetail: async (clubId) => api.get(`/faculty/clubs/${clubId}`),
  getEvents: async (userId, status) => api.get(`/faculty/${userId}/events${status ? `?status=${status}` : ''}`),
  decideEvent: async (eventId, decision) => api.patch(`/faculty/events/${eventId}/decision`, decision),
  getExpenses: async (userId, status) => api.get(`/faculty/${userId}/expenses${status ? `?status=${status}` : ''}`),
  decideExpense: async (expenseId, decision) => api.patch(`/faculty/expenses/${expenseId}/decision`, decision),
  getAnnouncements: async (userId) => api.get(`/faculty/${userId}/announcements`),
  postAnnouncement: async (data) => api.post('/faculty/announcements', data),
};
