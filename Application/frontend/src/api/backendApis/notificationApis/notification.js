import { api } from '../../api';

export const notificationApi = {
  getNotifications: async (userId) => {
    // Assuming backend endpoint is /users/{userId}/notifications or similar.
    // For now we map it to standard /notifications?user_id=X
    const res = await api.get(`/notifications?user_id=${userId}`);
    return res;
  },
  
  markAsRead: async (id) => {
    return await api.patch(`/notifications/${id}/read`, { is_read: true });
  },

  markAllAsRead: async (userId) => {
    return await api.post(`/notifications/read-all`, { user_id: userId });
  }
};
