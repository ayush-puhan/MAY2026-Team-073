import { api } from '../../api';

export const eventsRealApi = {
  getAllEvents: async () => {
    return await api.get('/events');
  },

  getEventById: async (id) => {
    return await api.get(`/events/${id}`);
  },

  registerForEvent: async (eventId, userId, isExternal, externalData = null) => {
    let result;
    
    let isPublic = false;
    try {
      const ev = await api.get(`/events/${eventId}`);
      if (ev?.data?.is_public || ev?.is_public) isPublic = true;
    } catch { }

    if (isExternal || isPublic) {
      result = await api.post(`/events/${eventId}/register-external`, externalData);
    } else {
      result = await api.post(`/events/${eventId}/register`);
    }

    // Trigger in-app notification + email simultaneously
    try {
      await api.post('/notifications', {
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
    const endpoint = isExternal ? `/users/${userId}/external-events` : `/users/${userId}/events`;
    return await api.get(endpoint);
  },

  unregisterFromEvent: async (eventId) => {
    return await api.del(`/events/${eventId}/register`);
  },

  getEventSessions: async (eventId) => {
    const res = await api.get(`/events/${eventId}/sessions`);
    return res;
  },

  createEventSessions: async (eventId, sessionsArray) => {
    const res = await api.post(`/events/${eventId}/sessions`, { sessions: sessionsArray });
    return res;
  },

  deleteEventSessions: async (eventId) => {
    const res = await api.delete(`/events/${eventId}/sessions`);
    return res;
  },

  getEventAttendance: async (eventId) => {
    const res = await api.get(`/events/${eventId}/attendance`);
    return res;
  },

  checkInUser: async (eventId, userId, recordedBy) => {
    const res = await api.post(`/events/${eventId}/attendance`, { user_id: userId, recorded_by: recordedBy });
    return res;
  },

  undoCheckIn: async (recordId) => {
    const res = await api.delete(`/attendance/${recordId}`);
    return res;
  }
};
