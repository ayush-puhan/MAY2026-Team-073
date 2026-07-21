import { api } from '../../api';

export const eventsRealApi = {
  getAllEvents: async () => {
    return await api.get('/api/events');
  },
  getEventById: async (id) => {
    return await api.get(`/api/events/${id}`);
  },
  registerForEvent: async (eventId, userId, isExternal, externalData = null) => {
    if (isExternal) {
      return await api.post(`/api/events/${eventId}/register-external`, externalData);
    } else {
      return await api.post(`/api/events/${eventId}/register`);
    }
  }
};
