import { api } from '../../api';

export const announcementsApi = {
  getAnnouncements: async (clubId = null) => {
    let endpoint = '/announcements';
    if (clubId) {
      if (clubId === 'university') {
        endpoint += '?type=university';
      } else {
        endpoint += `?club_id=${clubId}`;
      }
    }
    const data = await api.get(endpoint);
    return data;
  },

  getClubs: async () => {
    return await api.get('/clubs');
  },

  postAnnouncement: async (announcementData) => {
    return await api.post('/announcements', announcementData);
  },
};
