import { api } from '../../api';

export const adminRealApi = {
  getStats: async () => api.get('/admin/stats'),
  getRecentUsers: async () => api.get('/admin/users/recent'),
  getRecentTickets: async () => api.get('/admin/support/recent'),
  getAuditLogs: async (limit = 10) => api.get(`/admin/audit-logs?limit=${limit}`),
  
  // User Management
  getUsers: async () => api.get('/admin/users'),
  getUserById: async (id) => api.get(`/admin/users/${id}`),
  updateUserStatus: async (id, status) => api.patch(`/admin/users/${id}/status`, { status }),
  createUser: async (userData) => api.post('/admin/users', userData),
  
  // Roles & Permissions
  assignRole: async (userId, role) => api.patch(`/admin/users/${userId}/role`, { role }),
  getRoles: async () => api.get('/admin/roles'),
  getUsersByRole: async (role) => api.get(`/admin/users?role=${role}`),
  
  // Reports & Analytics
  getAnalytics: async (timeRange = 'month') => api.get(`/admin/analytics?range=${timeRange}`),
  
  // Platform Settings
  getPlatformSettings: async () => api.get('/admin/universities'),
  getUniversities: async () => api.get('/admin/universities'),
  createUniversity: async (data) => api.post('/admin/universities', data),
  updatePlatformSettings: async (id, settings) => api.patch(`/admin/universities/${id}`, settings),
  
  // Support Management
  getSupportTickets: async () => api.get('/admin/support'),
  getTicketById: async (id) => api.get(`/admin/support/${id}`),
  updateTicket: async (id, updates) => api.patch(`/admin/support/${id}`, updates),
  respondToTicket: async (id, responseMsg) => api.post(`/admin/support/${id}/respond`, { message: responseMsg })
};
