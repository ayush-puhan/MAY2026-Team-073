import { api } from '../../api';
import { logAudit } from '../auditHelper';
import { notificationApi } from '../notificationApis/notification';

// Helper to fetch normalized data and join it in memory
export const eventsMockApi = {
  getAllEvents: async () => {
    // 1. Fetch raw tables from json-server
    const [events, clubs, universities, eventInterests, interests, eventSessions] = await Promise.all([
      api.get('/events'),
      api.get('/clubs'),
      api.get('/universities'),
      api.get('/event_interests'),
      api.get('/interests'),
      api.get('/event_sessions')
    ]);

    // 2. Build lookup maps for performance
    const clubMap = clubs.reduce((acc, club) => {
      acc[club.id] = club;
      return acc;
    }, {});

    const uniMap = universities.reduce((acc, uni) => {
      acc[uni.id] = uni;
      return acc;
    }, {});

    const interestMap = interests.reduce((acc, interest) => {
      acc[interest.id] = interest;
      return acc;
    }, {});

    // 3. Map eventInterests to their event_ids
    const eventInterestsMap = eventInterests.reduce((acc, ei) => {
      if (!acc[ei.event_id]) acc[ei.event_id] = [];
      if (interestMap[ei.interest_id]) {
        acc[ei.event_id].push(interestMap[ei.interest_id]);
      }
      return acc;
    }, {});

    // 3b. Map eventSessions to their event_ids
    const eventSessionsMap = eventSessions.reduce((acc, es) => {
      if (!acc[es.event_id]) acc[es.event_id] = [];
      acc[es.event_id].push(es);
      return acc;
    }, {});

    // 4. Perform the join
    return events.map(event => {
      const club = clubMap[event.club_id];
      const university = club ? uniMap[club.university_id] : null;
      const eventInts = eventInterestsMap[event.id] || [];
      const sessions = eventSessionsMap[event.id] || [];

      // Auto-assign a banner keyword based on interests or category if not provided
      let bannerKeyword = event.banner;
      if (!bannerKeyword) {
        const checkStr = (event.category + ' ' + eventInts.map(i => i.name).join(' ')).toLowerCase();
        if (checkStr.includes('tech') || checkStr.includes('code') || checkStr.includes('hack')) bannerKeyword = 'tech';
        else if (checkStr.includes('music') || checkStr.includes('concert')) bannerKeyword = 'music';
        else if (checkStr.includes('robot')) bannerKeyword = 'robotics';
        else if (checkStr.includes('art') || checkStr.includes('cultur')) bannerKeyword = 'cultural';
        else if (checkStr.includes('financ') || checkStr.includes('business')) bannerKeyword = 'finance';
        else if (checkStr.includes('food') || checkStr.includes('cook')) bannerKeyword = 'food';
        else if (checkStr.includes('health') || checkStr.includes('mental')) bannerKeyword = 'mental_health';
        else if (checkStr.includes('photo') || checkStr.includes('camera')) bannerKeyword = 'camera';
        else bannerKeyword = 'cultural'; // default fallback
      }
      
      return {
        ...event,
        banner: bannerKeyword,
        club: club ? {
          ...club,
          university: university || null
        } : null,
        interests: eventInts,
        event_sessions: sessions
      };
    });
  },

  getEventById: async (id) => {
    // We can just reuse getAllEvents for mocking convenience
    const all = await eventsMockApi.getAllEvents();
    return all.find(e => String(e.id) === String(id));
  },

  registerForEvent: async (eventId, userId, isExternal, externalData = null) => {
    // Fetch event title for notification
    let eventTitle = '';
    let isPublic = false;
    try {
      const ev = await api.get(`/events/${eventId}`);
      eventTitle = ev?.title || `Event #${eventId}`;
      if (ev?.is_public) isPublic = true;
    } catch { eventTitle = `Event #${eventId}`; }

    // If user is external OR event is public, route to external_participants
    if (isExternal || isPublic) {
      // Duplicate check: same user + same event in external_participants
      if (userId) {
        const existingExternals = await api.get(`/external_participants?event_id=${eventId}&user_id=${userId}`);
        if (existingExternals && existingExternals.length > 0) {
          return existingExternals[0]; // Already registered
        }
      }

      const result = await api.post('/external_participants', {
        event_id: eventId,
        user_id: userId,
        full_name: externalData?.full_name,
        email: externalData?.email,
        affiliation: externalData?.affiliation || 'Campus Student',
        participant_type: externalData?.participant_type || 'other_university_student',
        registered_at: new Date().toISOString()
      });
      if (!userId) {
        throw new Error("Authentication required. Please log in to perform this action.");
      }
      await logAudit({
        userId: userId,
        action: 'CREATE',
        entityType: 'ExternalParticipant',
        entityId: result.id,
        details: `External participant registered for event #${eventId}: ${externalData.full_name}`
      });

      // Create in-app notification
      if (userId) {
        await notificationApi.createNotification({
          userId,
          type: 'EVENT_REMINDER',
          title: 'Event Registration Confirmed',
          body: `You have been registered for ${eventTitle}.`,
          channel: 'IN_APP',
          relatedEntityType: 'Event',
          relatedEntityId: eventId
        });
      }

      return result;
    } else {
      // Duplicate check: same user + same event in event_registrations
      const existingRegs = await api.get(`/event_registrations?event_id=${eventId}&user_id=${userId}`);
      if (existingRegs && existingRegs.length > 0) {
        return existingRegs[0]; // Already registered
      }

      const result = await api.post('/event_registrations', {
        event_id: eventId,
        user_id: userId,
        status: 'registered',
        registered_at: new Date().toISOString()
      });
      
      const allEvents = await eventsMockApi.getAllEvents();
      const event = allEvents.find(e => String(e.id) === String(eventId));
      const clubId = event?.club?.id || event?.club_id;
      
      const auditPayload = {
        userId,
        action: 'CREATE',
        entityType: 'EventRegistration',
        entityId: result.id,
        details: `User #${userId} registered for event #${eventId}`
      };
      if (clubId) auditPayload.club_id = clubId;
      
      await logAudit(auditPayload);

      // Create in-app notification
      await notificationApi.createNotification({
        userId,
        type: 'EVENT_REMINDER',
        title: 'Event Registration Confirmed',
        body: `You have been registered for ${event?.title || 'the event'}.`,
        channel: 'IN_APP',
        relatedEntityType: 'Event',
        relatedEntityId: eventId
      });

      return result;
    }
  },

  getUserEvents: async (userId, isExternal = false) => {
    let regEventIds = new Set();

    if (isExternal) {
      // Guest/Unverified user: only fetch from external_participants
      const externals = await api.get('/external_participants');
      const userExts = externals.filter(r => String(r.user_id) === String(userId));
      regEventIds = new Set(userExts.map(r => String(r.event_id)));
    } else {
      // Verified university student: fetch from both event_registrations and external_participants
      const [registrations, externals] = await Promise.all([
        api.get('/event_registrations'),
        api.get('/external_participants')
      ]);
      const userRegs = registrations.filter(r => String(r.user_id) === String(userId));
      const userExts = externals.filter(r => String(r.user_id) === String(userId));
      regEventIds = new Set([
        ...userRegs.map(r => String(r.event_id)),
        ...userExts.map(r => String(r.event_id))
      ]);
    }
    
    const allEvents = await eventsMockApi.getAllEvents();
    return allEvents.filter(e => regEventIds.has(String(e.id)));
  },

  getEventSessions: async (eventId) => {
    return api.get(`/event_sessions?event_id=${eventId}`);
  },

  createEventSessions: async (eventId, sessionsArray) => {
    await eventsMockApi.deleteEventSessions(eventId);
    const promises = sessionsArray.map(session => 
      api.post('/event_sessions', { ...session, event_id: eventId })
    );
    const results = await Promise.all(promises);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (!user.id) throw new Error("Authentication required. Please log in to perform this action.");
    
    await logAudit({
      userId: user.id,
      action: 'CREATE',
      entityType: 'EventSession',
      entityId: eventId,
      details: `Created/Updated ${sessionsArray.length} sessions for event #${eventId}`
    });
    
    return results;
  },

  deleteEventSessions: async (eventId) => {
    const existing = await eventsMockApi.getEventSessions(eventId);
    const promises = existing.map(session => 
      api.del(`/event_sessions/${session.id}`)
    );
    const results = await Promise.all(promises);
    
    if (existing.length > 0) {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (!user.id) throw new Error("Authentication required. Please log in to perform this action.");
      
      await logAudit({
        userId: user.id,
        action: 'DELETE',
        entityType: 'EventSession',
        entityId: eventId,
        details: `Deleted ${existing.length} old sessions for event #${eventId}`
      });
    }
    
    return results;
  },

  getEventAttendance: async (eventId) => {
    const [records, users] = await Promise.all([
      api.get(`/attendance_records?event_id=${eventId}`),
      api.get('/users')
    ]);
    const userMap = users.reduce((acc, user) => {
      acc[user.id] = user;
      return acc;
    }, {});
    return records.map(r => ({ ...r, user: userMap[r.user_id] }));
  },

  checkInUser: async (eventId, userId, recordedBy) => {
    const result = await api.post('/attendance_records', {
      event_id: eventId,
      user_id: userId,
      recorded_by: recordedBy,
      checked_in_at: new Date().toISOString()
    });

    await logAudit({
      userId: recordedBy,
      action: 'CREATE',
      entityType: 'AttendanceRecord',
      entityId: result.id,
      details: `Checked in user #${userId} for event #${eventId}`
    });

    return result;
  },

  undoCheckIn: async (recordId) => {
    const existing = await api.get(`/attendance_records/${recordId}`);
    const result = await api.del(`/attendance_records/${recordId}`);
    
    if (existing) {
      await logAudit({
        userId: existing.recorded_by,
        action: 'DELETE',
        entityType: 'AttendanceRecord',
        entityId: recordId,
        details: `Removed check-in record for user #${existing.user_id} at event #${existing.event_id}`
      });
    }
    
    return result;
  }
};
