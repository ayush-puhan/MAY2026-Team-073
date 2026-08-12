import { api } from '../../api';

export const eventsRealApi = {
  getAllEvents: async (params = {}) => {
    return await api.get('/events', { params });
  },

  getEventById: async (id) => {
    return await api.get(`/events/${id}`);
  },

  getEventDetails: async (id) => {
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
    return await api.get(`/events/${eventId}/sessions`);
  },

  createEventSessions: async (eventId, sessionsArray) => {
    return await api.post(`/events/${eventId}/sessions`, { sessions: sessionsArray });
  },

  deleteEventSessions: async (eventId) => {
    return await api.del(`/events/${eventId}/sessions`);
  },

  updateEventSession: async (sessionId, data) => {
    return await api.put(`/sessions/${sessionId}`, data);
  },

  deleteEventSession: async (sessionId) => {
    return await api.del(`/sessions/${sessionId}`);
  },

  getEventRegistrations: async (eventId) => {
    return await api.get(`/events/${eventId}/register`);
  },

  getExternalParticipants: async (eventId) => {
    return await api.get(`/events/${eventId}/register-external`);
  },

  getEventAttendance: async (eventId) => {
    return await api.get(`/events/${eventId}/attendance`);
  },

  checkInUser: async (eventId, userId, recordedBy) => {
    return await api.post(`/events/${eventId}/attendance`, { user_id: userId, recorded_by: recordedBy });
  },

  undoCheckIn: async (recordId) => {
    return await api.del(`/attendance/${recordId}`);
  }
};
