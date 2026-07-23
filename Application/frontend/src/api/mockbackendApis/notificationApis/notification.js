import { api } from '../../api';

export const notificationApi = {
  getNotifications: async (userId) => {
    // Run background simulators (cron mocks)
    await notificationApi.simulateBackgroundJobs(userId);
    // For json-server, use strict equality or fetch all and filter
    const res = await api.get(`/notifications?user_id=${userId}`);
    return res.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },
  
  simulateBackgroundJobs: async (userId) => {
    const now = new Date();
    const in48Hours = new Date(now.getTime() + 48 * 60 * 60 * 1000);
    
    // Simulate Deadline Approaching
    try {
      const allTasks = await api.get('/volunteer_assignments');
      const userTasks = allTasks.filter(t => 
        t.status === 'assigned' && 
        t.due_at && 
        new Date(t.due_at) > now && 
        new Date(t.due_at) < in48Hours
      );
      
      for (const task of userTasks) {
        const membership = await api.get(`/club_memberships/${task.assignee_membership_id}`);
        if (membership && String(membership.user_id) === String(userId)) {
          // Check if already notified
          const existing = await api.get(`/notifications?user_id=${userId}&type=DEADLINE_WARNING&related_entity_id=${task.id}`);
          if (!existing || existing.length === 0) {
            await notificationApi.createNotification({
              userId,
              type: 'DEADLINE_WARNING',
              title: 'Deadline Approaching',
              body: `Your task "${task.task_description}" is due soon!`,
              channel: 'IN_APP',
              relatedEntityType: 'VolunteerAssignment',
              relatedEntityId: task.id
            });
          }
        }
      }
    } catch (e) { console.error(e); }

    // Simulate Event Starting Soon
    try {
      const userRegs = await api.get(`/event_registrations?user_id=${userId}&status=registered`);
      const eventIds = userRegs.map(r => r.event_id);
      
      for (const eventId of eventIds) {
        const ev = await api.get(`/events/${eventId}`);
        if (ev && ev.start_at && new Date(ev.start_at) > now && new Date(ev.start_at) < in48Hours) {
          const existing = await api.get(`/notifications?user_id=${userId}&type=EVENT_STARTING&related_entity_id=${eventId}`);
          if (!existing || existing.length === 0) {
            await notificationApi.createNotification({
              userId,
              type: 'EVENT_STARTING',
              title: 'Event Starting Soon',
              body: `"${ev.title}" is starting within 48 hours!`,
              channel: 'IN_APP',
              relatedEntityType: 'Event',
              relatedEntityId: eventId
            });
          }
        }
      }
    } catch (e) { console.error(e); }
  },
  
  markAsRead: async (id) => {
    return await api.patch(`/notifications/${id}`, { is_read: true });
  },

  markAllAsRead: async (userId) => {
    const res = await api.get(`/notifications?user_id=${userId}`);
    const unread = res.filter(n => !n.is_read);
    await Promise.all(unread.map(n => api.patch(`/notifications/${n.id}`, { is_read: true })));
    return true;
  },

  createNotification: async ({ userId, type, title, body, channel = 'IN_APP', relatedEntityType = null, relatedEntityId = null }) => {
    return await api.post('/notifications', {
      user_id: userId,
      type: type,
      title: title,
      body: body,
      channel: channel,
      is_read: false,
      sent_via_resend: false,
      related_entity_type: relatedEntityType,
      related_entity_id: relatedEntityId,
      created_at: new Date().toISOString()
    });
  },

  sendEmail: async (userId, type, payload) => {
    // In mock mode, we just create an EMAIL-channel notification as a placeholder.
    // The real backend would trigger an actual email via SMTP/Resend.
    return await api.post('/notifications', {
      user_id: userId,
      type: type,
      title: payload.subject || 'Email Notification',
      body: payload.body || payload.message || '',
      channel: 'EMAIL',
      is_read: false,
      sent_via_resend: true,
      related_entity_type: payload.relatedEntityType || null,
      related_entity_id: payload.relatedEntityId || null,
      created_at: new Date().toISOString()
    });
  }
};
