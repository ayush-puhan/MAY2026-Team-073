import { api } from '../../api';

export const calendarRealApi = {
  /**
   * Fetches all event sessions relevant to the user.
   * The backend handles all access control and filtering logic natively via SQL.
   */
  getCalendarEvents: async (userId, filters = {}) => {
    try {
      // Create query params
      const params = new URLSearchParams();
      if (filters.show_public !== undefined) params.append('show_public', filters.show_public);
      if (filters.university_id) params.append('university_id', filters.university_id);
      if (filters.club_id) params.append('club_id', filters.club_id);

      const response = await api.get(`/calendar/events?${params.toString()}`);
      
      // Map to react-big-calendar expected format
      const formattedSessions = response.map(session => ({
        id: `session-${session.session_id}`,
        sessionId: session.session_id,
        sessionTitle: session.session_title,
        eventId: session.event_id,
        eventTitle: session.event_title,
        clubId: session.club_id,
        clubName: session.club_name,
        clubLogo: session.club_logo,
        universityId: session.university_id,
        venue: session.venue,
        start: new Date(session.start_at),
        end: new Date(session.end_at),
        isPublic: session.is_public,
        isRegistered: session.is_registered,
        hasConflict: session.has_conflict,
        status: session.status,
        color: session.is_public ? 'var(--innovation)' : 'var(--primary)'
      }));

      return formattedSessions;
    } catch (error) {
      console.error("Error fetching real calendar events:", error);
      throw error;
    }
  },

  getEventSessionsByEvent: async (eventId) => {
    const response = await api.get(`/events/${eventId}/sessions`);
    return response;
  },

  createEventSession: async (eventId, data) => {
    const response = await api.post(`/events/${eventId}/sessions`, data);
    return response;
  },

  updateEventSession: async (sessionId, data) => {
    const response = await api.patch(`/event-sessions/${sessionId}`, data);
    return response;
  },

  deleteEventSession: async (sessionId) => {
    await api.del(`/event-sessions/${sessionId}`);
    return true;
  },

  syncToGoogleCalendar: async (userId) => {
    const response = await api.post(`/calendar/sync-google`, {});
    return response;
  }
};
