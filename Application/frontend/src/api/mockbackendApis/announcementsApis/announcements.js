import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

export const announcementsApi = {
  // Fetch all announcements.
  getAnnouncements: async (clubId = null) => {
    let endpoint = '/announcements';
    if (clubId) {
      if (clubId === 'university') {
        const all = await api.get(endpoint);
        return all.filter(a => !a.club_id);
      }
      endpoint += `?club_id=${clubId}`;
    }
    const data = await api.get(endpoint);
    // Sort descending by date
    return data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  getClubs: async () => {
    return await api.get('/clubs');
  },

  // Post a new announcement
  postAnnouncement: async (announcementData) => {
    const payload = {
      ...announcementData,
      created_at: istNow(),
    };
    const created = await api.post('/announcements', payload);
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'CREATE',
      entityType: 'Announcement',
      entityId: created.id,
      details: `Posted announcement: ${announcementData.title}`,
    });
    return created;
  },
};
