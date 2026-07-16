import { api } from '../../api';

const toId = (id) => (/^\d+$/.test(String(id)) ? parseInt(id, 10) : id);

const slugify = (name) =>
  name.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

const notify = (userId, title, body) =>
  api.post('/notifications', {
    user_id: toId(userId),
    title,
    body,
    is_read: 0,
    created_at: new Date().toISOString(),
  });

export const universityAdminMockApi = {
  getStats: async () => {
    const [clubs, memberships, events, requests] = await Promise.all([
      api.get('/clubs'),
      api.get('/club_memberships?status=approved'),
      api.get('/events'),
      api.get('/club_creation_requests?status=submitted'),
    ]);

    return {
      totalClubs: clubs.filter((c) => c.status === 'active').length,
      totalMemberships: memberships.length,
      activeEvents: events.filter((e) => e.status === 'scheduled').length,
      pendingApprovals: requests.length,
    };
  },

  getClubCreationRequests: async (status) => {
    const requests = await api.get(status ? `/club_creation_requests?status=${status}` : '/club_creation_requests');
    const users = await api.get('/users');
    return requests
      .map((r) => ({
        ...r,
        requested_by_name: users.find((u) => toId(u.id) === toId(r.requested_by))?.full_name || 'Unknown',
      }))
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  decideClubCreationRequest: async (id, { status, reviewed_by, review_comments, faculty_advisor_id }) => {
    const request = await api.get(`/club_creation_requests/${toId(id)}`);
    let resultingClubId = request.resulting_club_id;

    if (status === 'approved') {
      const newClub = await api.post('/clubs', {
        name: request.proposed_name,
        slug: slugify(request.proposed_name),
        category: request.proposed_category,
        description: request.proposal_description,
        objectives: null,
        logo_url: null,
        status: 'active',
        faculty_advisor_id: toId(faculty_advisor_id),
        member_count_cache: 0,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null,
      });
      resultingClubId = newClub.id;
    }

    const updatedRequest = await api.patch(`/club_creation_requests/${toId(id)}`, {
      status,
      reviewed_by: toId(reviewed_by),
      review_comments,
      resulting_club_id: resultingClubId,
      decided_at: new Date().toISOString(),
    });

    await notify(
      request.requested_by,
      `Club Proposal ${status === 'approved' ? 'Approved' : 'Rejected'}`,
      `Your proposal "${request.proposed_name}" was ${status}.`
    );

    return updatedRequest;
  },

  getPendingClubActivations: async () => {
    const clubs = await api.get('/clubs?status=pending');
    return clubs.filter((c) => !c.faculty_advisor_id);
  },

  activateClub: async (clubId, facultyAdvisorId) =>
    api.patch(`/clubs/${toId(clubId)}`, {
      status: 'active',
      faculty_advisor_id: toId(facultyAdvisorId),
      updated_at: new Date().toISOString(),
    }),

  getFacultyAdvisors: async () => {
    const users = await api.get('/users?role=faculty_advisor');
    return users.map((u) => ({ value: toId(u.id), label: u.full_name }));
  },

  getAllClubs: async () => api.get('/clubs'),

  getAllEvents: async () => {
    const [events, clubs] = await Promise.all([api.get('/events'), api.get('/clubs')]);
    return events.map((e) => ({
      ...e,
      club_name: clubs.find((c) => toId(c.id) === toId(e.club_id))?.name || 'Unknown',
    }));
  },

  getAnalytics: async () => {
    const [clubs, memberships] = await Promise.all([
      api.get('/clubs'),
      api.get('/club_memberships?status=approved'),
    ]);

    const categoryMap = {};
    clubs.forEach((c) => {
      categoryMap[c.category] = (categoryMap[c.category] || 0) + 1;
    });
    const categoryDistribution = Object.entries(categoryMap).map(([category, count]) => ({ category, count }));

    const monthKey = (dateStr) => (dateStr || '').substring(0, 7);
    const growthMap = {};
    clubs.forEach((c) => {
      const key = monthKey(c.created_at);
      growthMap[key] = (growthMap[key] || 0) + 1;
    });
    const clubGrowth = Object.entries(growthMap)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, count]) => ({ month, count }));

    const membershipGrowthMap = {};
    memberships.forEach((m) => {
      const key = monthKey(m.applied_at);
      membershipGrowthMap[key] = (membershipGrowthMap[key] || 0) + 1;
    });
    const membershipGrowth = Object.entries(membershipGrowthMap)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, count]) => ({ month, count }));

    return { categoryDistribution, clubGrowth, membershipGrowth };
  },

  getAnnouncements: async () => {
    const announcements = await api.get('/announcements');
    return announcements
      .filter((a) => a.club_id === null || a.club_id === undefined)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  postAnnouncement: async ({ posted_by, title, body, target_audience }) =>
    api.post('/announcements', {
      club_id: null,
      posted_by: toId(posted_by),
      title,
      body,
      target_audience: target_audience || 'all_students',
      created_at: new Date().toISOString(),
    }),
};
