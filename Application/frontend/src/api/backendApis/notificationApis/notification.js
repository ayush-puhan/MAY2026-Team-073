import { api } from '../../api';

export const notificationApi = {
  getNotifications: async (userId) => {
    // Fetch all notifications including read ones for the NotificationsView
    const res = await api.get(`/notifications?user_id=${userId}&is_read=all`);
    return res;
  },
  
  markAsRead: async (id) => {
    return await api.patch(`/notifications/${id}/read`, { is_read: true });
  },

  markAllAsRead: async (userId) => {
    return await api.post(`/notifications/read-all`, { user_id: userId });
  },

  createNotification: async ({ userId, type, title, body, channel = 'IN_APP', relatedEntityType = null, relatedEntityId = null }) => {
    return await api.post('/notifications', {
      user_id: userId,
      type: type,
      title: title,
      body: body,
      channel: channel,
      related_entity_type: relatedEntityType,
      related_entity_id: relatedEntityId
    });
  },

  sendEmail: async (userId, type, payload) => {
    // Calls the backend email-sending endpoint.
    // The backend should handle SMTP/Resend integration.
    return await api.post('/notifications/email', {
      user_id: userId,
      type: type,
      subject: payload.subject || 'ClubConnect Notification',
      body: payload.body || payload.message || '',
      email: payload.email || null,
      related_entity_type: payload.relatedEntityType || null,
      related_entity_id: payload.relatedEntityId || null
    });
  }
};
