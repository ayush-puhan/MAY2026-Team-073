import axios from 'axios';
import { logAudit, istNow } from '../auditHelper';

const MOCK_URL = import.meta.env.VITE_MOCK_API_URL || 'http://localhost:5000';

/**
 * Validates visibility rules for a given user.
 */
const canUserSeeEvent = (event, user, userMemberships) => {
  // If it's a cross-university public event
  if (event.is_public) {
    return true; // The UI toggle will handle cross-university filtering
  }

  // System admin only sees public events (which was handled above)
  if (user.role === 'system_admin') {
    return false;
  }

  // Same university logic
  const club = event.club; // Assuming club is joined
  if (club && club.university_id === user.university_id) {
    if (event.is_public) {
      return true; // University-wide public event
    }
  }

  // Private club event -> check membership
  const isMember = userMemberships.some(m => m.club_id === event.club_id && m.status === 'approved');
  if (isMember) {
    return true;
  }

  return false;
};

export const calendarMockApi = {
  /**
   * Fetches all event sessions relevant to the user.
   */
  getCalendarEvents: async (userId, filters = {}) => {
    try {
      // 1. Fetch user to know role and university
      let { data: users } = await axios.get(`${MOCK_URL}/users?id=${userId}`);
      if (!users.length) {
        console.warn(`User ${userId} not found in mock DB. Falling back to default user.`);
        const { data: allUsers } = await axios.get(`${MOCK_URL}/users`);
        users = allUsers;
      }
      if (!users.length) throw new Error("User not found");
      const user = users[0];

      // 2. Fetch user's club memberships
      const { data: memberships } = await axios.get(`${MOCK_URL}/club_memberships?user_id=${userId}`);
      
      // 3. Fetch user's registrations (to compute hasConflict and isRegistered)
      const { data: registrations } = await axios.get(`${MOCK_URL}/event_registrations?user_id=${userId}`);
      const registeredEventIds = new Set(registrations.map(r => r.event_id));

      // 4. Fetch all events and their clubs (using JSON Server's _expand)
      const { data: events } = await axios.get(`${MOCK_URL}/events?_expand=club`);

      // 5. Filter events based on strict access control logic
      let visibleEvents = events.filter(ev => {
        // Must check if user can see it
        const canSee = canUserSeeEvent(ev, user, memberships);
        
        // Always show if user is registered (even if they left the club later, etc.)
        if (registeredEventIds.has(ev.id)) return true;
        
        return canSee;
      });

      // 6. Apply UI filters (Public toggle, University, Club)
      if (filters.show_public !== undefined && !filters.show_public) {
        // If show_public is false, exclude events from OTHER universities
        visibleEvents = visibleEvents.filter(ev => {
          return (ev.club && ev.club.university_id === user.university_id) || user.role === 'system_admin';
        });
      }
      
      if (filters.university_id) {
        visibleEvents = visibleEvents.filter(ev => ev.club && ev.club.university_id === parseInt(filters.university_id));
      }

      if (filters.club_id) {
        visibleEvents = visibleEvents.filter(ev => ev.club_id === parseInt(filters.club_id));
      }

      const visibleEventIds = new Set(visibleEvents.map(e => parseInt(e.id)));

      // 7. Fetch all event sessions
      const { data: sessions } = await axios.get(`${MOCK_URL}/event_sessions`);

      // 8. Map to react-big-calendar expected format
      const formattedSessions = [];
      const userRegisteredSessions = [];

      sessions.forEach(session => {
        if (!visibleEventIds.has(parseInt(session.event_id))) return;

        const parentEvent = visibleEvents.find(e => parseInt(e.id) === parseInt(session.event_id));
        const isRegistered = registeredEventIds.has(parseInt(parentEvent.id));

        const sessionObj = {
          id: `session-${session.id}`,
          sessionId: parseInt(session.id),
          sessionTitle: session.title,
          eventId: parseInt(parentEvent.id),
          eventTitle: parentEvent.title,
          clubId: parentEvent.club_id,
          clubName: parentEvent.club?.name,
          clubLogo: parentEvent.club?.logo_url,
          universityId: parentEvent.club?.university_id,
          venue: session.venue || parentEvent.venue,
          start: new Date(session.start_at),
          end: new Date(session.end_at),
          isPublic: parentEvent.is_public === 1 || parentEvent.is_public === true,
          isRegistered,
          hasConflict: false,
          status: parentEvent.status,
          color: (parentEvent.is_public === 1 || parentEvent.is_public === true) ? 'var(--innovation)' : 'var(--primary)'
        };

        if (isRegistered) {
          userRegisteredSessions.push(sessionObj);
        }

        formattedSessions.push(sessionObj);
      });

      // 9. Compute conflicts among user's registered sessions
      for (let i = 0; i < userRegisteredSessions.length; i++) {
        for (let j = i + 1; j < userRegisteredSessions.length; j++) {
          const s1 = userRegisteredSessions[i];
          const s2 = userRegisteredSessions[j];
          
          // Check overlap
          if (s1.start < s2.end && s2.start < s1.end) {
            s1.hasConflict = true;
            s2.hasConflict = true;
          }
        }
      }

      return formattedSessions;

    } catch (error) {
      console.error("Error fetching mock calendar events:", error);
      throw error;
    }
  },

  getEventSessionsByEvent: async (eventId) => {
    const { data } = await axios.get(`${MOCK_URL}/event_sessions?event_id=${eventId}`);
    return data;
  },

  createEventSession: async (eventId, data) => {
    const response = await axios.post(`${MOCK_URL}/event_sessions`, {
      ...data,
      event_id: eventId,
      created_at: istNow()
    });
    
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'CREATE',
      entityType: 'EventSession',
      entityId: response.data.id,
      details: `Created event session: ${data.title} for Event #${eventId}`,
    });
    
    return response.data;
  },

  updateEventSession: async (sessionId, data) => {
    const response = await axios.patch(`${MOCK_URL}/event_sessions/${sessionId}`, data);
    
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'UPDATE',
      entityType: 'EventSession',
      entityId: sessionId,
      details: `Updated event session #${sessionId}`,
    });
    
    return response.data;
  },

  deleteEventSession: async (sessionId) => {
    await axios.delete(`${MOCK_URL}/event_sessions/${sessionId}`);
    
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'DELETE',
      entityType: 'EventSession',
      entityId: sessionId,
      details: `Deleted event session #${sessionId}`,
    });
    
    return true;
  },

  syncToGoogleCalendar: async (userId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true, message: "Google sync simulated successfully in mock mode." });
      }, 1500);
    });
  }
};
