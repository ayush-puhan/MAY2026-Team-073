import { api } from '../../api';

export const notificationMockApi = {
  getNotifications: async (userId) => {
    // For json-server, use strict equality or fetch all and filter
    const res = await api.get(`/notifications?user_id=${userId}`);
    return res.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },
  
  markAsRead: async (id) => {
    return await api.patch(`/notifications/${id}`, { is_read: true });
  },

  markAllAsRead: async (userId) => {
    const res = await api.get(`/notifications?user_id=${userId}`);
    const unread = res.filter(n => !n.is_read);
    await Promise.all(unread.map(n => api.patch(`/notifications/${n.id}`, { is_read: true })));
    return true;
  }
};
