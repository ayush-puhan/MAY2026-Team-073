import { api } from '../../api';

export const emergencyApi = {
  submitEmergencyReport: async (data) => {
    const res = await api.post('/emergency-reports', data);
    return res.data;
  },

  getEmergencyReports: async (filters = {}) => {
    const queryParams = new URLSearchParams(filters).toString();
    const res = await api.get(`/emergency-reports${queryParams ? `?${queryParams}` : ''}`);
    return res.data;
  },

  updateEmergencyStatus: async (reportId, status, handledBy) => {
    const res = await api.patch(`/emergency-reports/${reportId}/status`, { status, handled_by: handledBy });
    return res.data;
  },

  getActiveEmergencies: async () => {
    const res = await api.get('/emergency-reports/active');
    return res.data;
  }
};
