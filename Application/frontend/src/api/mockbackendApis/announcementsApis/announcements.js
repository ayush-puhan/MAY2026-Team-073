import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

import moment from 'moment';

export const announcementsApi = {
  // Fetch all announcements.
  getAnnouncements: async (clubId = null) => {
    let endpoint = '/announcements';
    const all = await api.get('/announcements');
    let data = [];
    if (clubId) {
      const parsedClubId = /^\d+$/.test(String(clubId)) ? parseInt(clubId, 10) : clubId;
      if (parsedClubId === 'university') {
        data = all.filter(a => !a.club_id);
      } else {
        data = all.filter(a => {
           const dbClubId = /^\d+$/.test(String(a.club_id)) ? parseInt(a.club_id, 10) : String(a.club_id);
           const queryClubId = /^\d+$/.test(String(parsedClubId)) ? parseInt(parsedClubId, 10) : String(parsedClubId);
           return dbClubId === queryClubId;
        });
      }
    } else {
      data = all;
    }
    
    const users = await api.get('/users');
    
    // Format and sort descending by date
    return data
      .map(a => ({
        ...a,
        content: a.body,
        author_name: users.find(u => String(u.id) === String(a.posted_by))?.full_name || 'Unknown',
        time: moment(a.created_at).fromNow()
      }))
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  getClubs: async () => {
    return await api.get('/clubs');
  },

  postAnnouncement: async (announcementData) => {
    const payload = {
      ...announcementData,
      club_id: announcementData.club_id ? parseInt(announcementData.club_id, 10) : undefined,
      posted_by: announcementData.posted_by ? parseInt(announcementData.posted_by, 10) : undefined,
      created_at: istNow(),
    };
    const created = await api.post('/announcements', payload);
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    if (!currentUser.id) throw new Error('User not authenticated');
    
    await logAudit({
      userId: currentUser.id,
      action: 'CREATE',
      entityType: 'Announcement',
      entityId: created.id,
      details: `Posted announcement: ${announcementData.title}`,
    });

    if (payload.club_id) {
      try {
        const { notificationApi } = await import('../notificationApis/notification.js');
        const memberships = await api.get(`/club_memberships?club_id=${payload.club_id}&status=approved`);
        const club = await api.get(`/clubs/${payload.club_id}`);
        for (const m of memberships) {
          let shouldNotify = true;
          
          if (payload.target_audience === 'targeted') {
            if (payload.target_role && payload.target_role !== 'ALL' && m.role_in_club !== payload.target_role) {
              shouldNotify = false;
            }
            if (payload.target_committee && payload.target_committee !== 'ALL' && String(m.committee_id) !== String(payload.target_committee)) {
              shouldNotify = false;
            }
          }
          
          if (shouldNotify && String(m.user_id) !== String(currentUser.id)) {
            await notificationApi.createNotification({
              userId: m.user_id,
              type: 'CLUB_UPDATE',
              title: `New Announcement from ${club.name}`,
              body: payload.title,
              channel: 'IN_APP',
              relatedEntityType: 'Announcement',
              relatedEntityId: created.id
            });
          }
        }
      } catch (e) { console.error('Notification error:', e); }
    }

    return created;
  },
};
