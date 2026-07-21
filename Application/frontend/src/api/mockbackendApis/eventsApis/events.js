import { api } from '../../api';
import { logAudit } from '../auditHelper';

// Helper to fetch normalized data and join it in memory
export const eventsMockApi = {
  getAllEvents: async () => {
    // 1. Fetch raw tables from json-server
    const [events, clubs, universities, eventInterests, interests] = await Promise.all([
      api.get('/events'),
      api.get('/clubs'),
      api.get('/universities'),
      api.get('/event_interests'),
      api.get('/interests')
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

    // 4. Perform the join
    return events.map(event => {
      const club = clubMap[event.club_id];
      const university = club ? uniMap[club.university_id] : null;
      const eventInts = eventInterestsMap[event.id] || [];

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
        interests: eventInts
      };
    });
  },

  getEventById: async (id) => {
    // We can just reuse getAllEvents for mocking convenience
    const all = await eventsMockApi.getAllEvents();
    return all.find(e => e.id === Number(id));
  },

  registerForEvent: async (eventId, userId, isExternal, externalData = null) => {
    if (isExternal) {
      const result = await api.post('/external_participants', {
        event_id: eventId,
        full_name: externalData.full_name,
        email: externalData.email,
        affiliation: externalData.affiliation,
        participant_type: externalData.participant_type,
        registered_at: new Date().toISOString()
      });
      await logAudit({
        userId: userId || 0,
        action: 'CREATE',
        entityType: 'ExternalParticipant',
        entityId: result.id,
        details: `External participant registered for event #${eventId}: ${externalData.full_name}`
      });
      return result;
    } else {
      const result = await api.post('/event_registrations', {
        event_id: eventId,
        user_id: userId,
        status: 'registered',
        registered_at: new Date().toISOString()
      });
      await logAudit({
        userId,
        action: 'CREATE',
        entityType: 'EventRegistration',
        entityId: result.id,
        details: `User #${userId} registered for event #${eventId}`
      });
      return result;
    }
  }
};
