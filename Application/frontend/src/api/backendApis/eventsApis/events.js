import { api } from '../../api';

export const eventsRealApi = {
  getAllEvents: async () => {
    return await api.get('/api/events');
  },

  getEventById: async (id) => {
    return await api.get(`/api/events/${id}`);
  },

  registerForEvent: async (eventId, userId, isExternal, externalData = null) => {
    let result;
    
    let isPublic = false;
    try {
      const ev = await api.get(`/api/events/${eventId}`);
      if (ev?.data?.is_public || ev?.is_public) isPublic = true;
    } catch { }

    if (isExternal || isPublic) {
      result = await api.post(`/api/events/${eventId}/register-external`, externalData);
    } else {
      result = await api.post(`/api/events/${eventId}/register`);
    }

    // Trigger in-app notification + email simultaneously
    try {
      await api.post('/api/notifications', {
        type: 'EVENT_REMINDER',
        title: 'Event Registration Confirmed',
        body: `You have been registered for event #${eventId}.`,
        channel: 'BOTH',
        related_entity_type: 'Event',
        related_entity_id: eventId
      });
    } catch (err) {
      console.error('Failed to create registration notification', err);
    }

    return result;
  },

  getUserEvents: async (userId, isExternal = false) => {
    const endpoint = isExternal ? `/api/users/${userId}/external-events` : `/api/users/${userId}/events`;
    return await api.get(endpoint);
  },

  unregisterFromEvent: async (eventId) => {
    return await api.del(`/api/events/${eventId}/register`);
  },

  getEventSessions: async (eventId) => {
    const res = await api.get(`/api/events/${eventId}/sessions`);
    return res.data;
  },

  createEventSessions: async (eventId, sessionsArray) => {
    const res = await api.post(`/api/events/${eventId}/sessions`, { sessions: sessionsArray });
    return res.data;
  },

  deleteEventSessions: async (eventId) => {
    const res = await api.delete(`/api/events/${eventId}/sessions`);
    return res.data;
  },

  getEventAttendance: async (eventId) => {
    const res = await api.get(`/api/events/${eventId}/attendance`);
    return res.data;
  },

  checkInUser: async (eventId, userId, recordedBy) => {
    const res = await api.post(`/api/events/${eventId}/attendance`, { user_id: userId, recorded_by: recordedBy });
    return res.data;
  },

  undoCheckIn: async (recordId) => {
    const res = await api.delete(`/api/attendance/${recordId}`);
    return res.data;
  }
};
