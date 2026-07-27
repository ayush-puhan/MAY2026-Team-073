import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

export const adminApi = {
  // Stats & Dashboard
  getStats: async () => {
    const [users, clubs, events, tickets] = await Promise.all([
      api.get('/users'),
      api.get('/clubs'),
      api.get('/events'),
      api.get('/support_tickets')
    ]);

    const calculateTrend = (items, dateField, periodDays) => {
      const now = new Date();
      const currentPeriodStart = new Date(now.getTime() - periodDays * 24 * 60 * 60 * 1000);
      const previousPeriodStart = new Date(now.getTime() - 2 * periodDays * 24 * 60 * 60 * 1000);

      const currentCount = items.filter(item => item[dateField] && new Date(item[dateField]) >= currentPeriodStart).length;
      const previousCount = items.filter(item => {
        if (!item[dateField]) return false;
        const date = new Date(item[dateField]);
        return date >= previousPeriodStart && date < currentPeriodStart;
      }).length;

      if (previousCount === 0) return currentCount > 0 ? 100 : 0;
      return Math.round(((currentCount - previousCount) / previousCount) * 100);
    };

    const stats = {
      totalUsers: users.length,
      activeUsers: users.filter(u => u.is_active).length,
      totalClubs: clubs.length,
      totalEvents: events.length,
      openTickets: tickets.filter(t => t.status === 'Open' || t.status === 'In Progress' || t.status === 'OPEN').length,
      userTrend: calculateTrend(users, 'created_at', 30), // vs last month
      eventsTrend: calculateTrend(events, 'created_at', 180), // vs last semester
      ticketsTrend: calculateTrend(tickets, 'created_at', 7), // vs last week
    };
    return stats;
  },

  getRecentUsers: async (limit = 5) => {
    const users = await api.get('/users');
    return users.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, limit);
  },

  getRecentTickets: async (limit = 5) => {
    const tickets = await api.get('/support_tickets');
    return tickets.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, limit);
  },

  getAuditLogs: async (limit = 10) => {
    try {
      const logs = await api.get('/audit_logs');
      return logs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, limit);
    } catch (err) {
      console.warn("Audit logs table might not exist in json-server yet.");
      return [];
    }
  },

  // User Management
  getUsers: async (filters = {}) => {
    let endpoint = '/users';
    // Simplified filtering for mock
    if (filters.role) endpoint += `?role=${filters.role}`;
    const users = await api.get(endpoint);
    return users;
  },

  getUserById: async (id) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const [user, spArr] = await Promise.all([
      api.get(`/users/${parsedId}`),
      api.get(`/student_profiles?user_id=${parsedId}`)
    ]);
    if (user && spArr && spArr.length > 0) {
      user.student_profile = spArr[0];
    }
    return user;
  },

  updateUserStatus: async (id, isActive) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const result = await api.patch(`/users/${parsedId}`, { is_active: isActive });
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'UPDATE',
      entityType: 'User',
      entityId: parsedId,
      details: `${isActive ? 'Activated' : 'Deactivated'} user #${parsedId} (${result.full_name || result.email})`,
    });
    return result;
  },

  assignRole: async (id, role) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const result = await api.patch(`/users/${parsedId}`, { role: role });
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'UPDATE',
      entityType: 'User',
      entityId: parsedId,
      details: `Changed role of user #${parsedId} to "${role}"`,
    });
    return result;
  },

  createUser: async (userData) => {
    // 1. Fetch current users to calculate the next integer ID
    const users = await api.get('/users');
    const maxId = users.reduce((max, u) => {
      const numId = parseInt(u.id, 10);
      return !isNaN(numId) && numId > max ? numId : max;
    }, 0);
    const newId = (maxId + 1).toString(); // use string representation of int

    // 2. Determine university_id if not explicitly provided
    let finalUniversityId = userData.university_id;
    if (!finalUniversityId && userData.email) {
      const emailDomain = userData.email.split('@')[1]?.toLowerCase();
      if (emailDomain) {
        // Fetch universities to check allowed_domains
        try {
          const universities = await api.get('/universities');
          const matchedUni = universities.find(uni => 
            uni.allowed_domains && uni.allowed_domains.some(d => d.domain.toLowerCase() === emailDomain)
          );
          if (matchedUni) {
            finalUniversityId = matchedUni.id;
          }
        } catch (e) {
          console.warn("Failed to auto-detect university domain", e);
        }
      }
    }

    // Generate mock auto-password
    const password = 'Temp@' + Math.random().toString(36).slice(-6) + '1';
    const newUser = {
      ...userData,
      id: newId,
      university_id: finalUniversityId || null,
      password_hash: password,
      auth_provider: "LOCAL",
      is_active: true,
      email_verified: true,
      created_at: istNow()
    };
    const created = await api.post('/users', newUser);
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'CREATE',
      entityType: 'User',
      entityId: created.id,
      details: `Created new user: ${userData.full_name} (${userData.email}) with role "${userData.role}"`,
    });
    // Attach the auto-generated password so the UI can show it temporarily
    return { ...created, _tempPassword: password };
  },

  deleteUser: async (id) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    
    // Attempt to fetch user to get name/email for logs
    let userDetails = '';
    try {
      const user = await api.get(`/users/${parsedId}`);
      if (user) userDetails = `${user.full_name || user.email}`;
    } catch(e) {}
    
    // In json-server, this deletes the user. (A real backend would cascade delete related data).
    await api.del(`/users/${parsedId}`);
    
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'DELETE',
      entityType: 'User',
      entityId: parsedId,
      details: `Deleted user #${parsedId} (${userDetails})`,
    });
    return true;
  },

  // Roles & Permissions
  getRoles: async () => {
    // Hardcoded roles for platform
    return [
      { id: 'student', name: 'Student', description: 'Standard user access' },
      { id: 'faculty_advisor', name: 'Faculty Advisor', description: 'Advisor access for specific clubs' },
      { id: 'student_affairs_office', name: 'Student Affairs Office', description: 'University level event approvals' },
      { id: 'dean_student_welfare', name: 'Dean of Student Welfare', description: 'University level club approvals' },
      { id: 'system_admin', name: 'System Administrator', description: 'Full platform access' }
    ];
  },

  getUsersByRole: async (role) => {
    return await api.get(`/users?role=${encodeURIComponent(role)}`);
  },

  // Analytics (Aggregations from existing tables)
  getAnalytics: async (type) => {
    if (type === 'platformAnalytics') {
      const users = await api.get('/users');
      // Group users by creation month mock
      const growth = {};
      users.forEach(u => {
        const dateStr = u.created_at || '2026-01-01T00:00:00.000Z';
        const month = dateStr.substring(0, 7); // YYYY-MM
        growth[month] = (growth[month] || 0) + 1;
      });
      return { growth };
    }
    return {};
  },

  logAuditAction: async (action, entity_type, entity_id, details) => {
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action,
      entityType: entity_type,
      entityId: entity_id,
      details,
    });
  },

  // Platform Settings
  getPlatformSettings: async (universityId = 1) => {
    try {
      const uni = await api.get(`/universities/${universityId}`);
      // Merge with default mock UI settings (these aren't in the DB schema)
      return {
        ...uni,
        defaultTheme: 'dark',
        passwordMinLength: 8,
        requireSpecialChar: true,
      };
    } catch (e) {
      return {
        name: 'ClubConnect University',
        domain: 'example.edu',
        defaultTheme: 'dark'
      };
    }
  },

  updatePlatformSettings: async (id, data) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const uniPatch = { name: data.name, domain: data.domain, is_active: data.is_active };
    if (data.banner !== undefined) {
      uniPatch.banner = data.banner;
    }
    await api.patch(`/universities/${parsedId}`, uniPatch);
    await adminApi.logAuditAction('update', 'university', parsedId, `Updated university settings: ${JSON.stringify(uniPatch)}`);
    return true;
  },

  getUniversities: async () => {
    return await api.get('/universities');
  },

  createUniversity: async (data) => {
    const newUni = {
      ...data,
      created_at: istNow()
    };
    const created = await api.post('/universities', newUni);
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'CREATE',
      entityType: 'University',
      entityId: created.id,
      details: `Created university: ${data.name}`,
    });
    return created;
  },

  // Support Management
  getSupportTickets: async (filters = {}) => {
    const [tickets, users] = await Promise.all([
      api.get('/support_tickets'),
      api.get('/users')
    ]);
    // Attach user objects to tickets for the table view
    return tickets.map(ticket => {
      const user = users.find(u => String(u.id) === String(ticket.raised_by));
      if (user) ticket.raised_by_user = user;
      return ticket;
    });
  },

  getTicketById: async (id) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const ticket = await api.get(`/support_tickets/${parsedId}`);
    if (ticket && ticket.raised_by) {
      try {
        const user = await api.get(`/users/${ticket.raised_by}`);
        ticket.raised_by_user = user;
      } catch (e) {
        console.warn("Could not fetch user for ticket", e);
      }
    }
    return ticket;
  },

  updateTicket: async (id, data) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const result = await api.patch(`/support_tickets/${parsedId}`, data);
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    await logAudit({
      userId: currentUser.id || 7,
      action: 'UPDATE',
      entityType: 'SupportTicket',
      entityId: parsedId,
      details: `Updated ticket #${parsedId}: ${JSON.stringify(data)}`,
    });
    return result;
  },

  respondToTicket: async (id, message) => {
    const parsedId = /^\d+$/.test(String(id)) ? parseInt(id, 10) : id;
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await api.post(`/ticket_responses`, {
      ticket_id: parsedId,
      responder_id: currentUser.id || 7,
      message: message,
      created_at: istNow()
    });
    await logAudit({
      userId: currentUser.id || 7,
      action: 'RESPOND',
      entityType: 'SupportTicket',
      entityId: parsedId,
      details: `Responded to ticket #${parsedId}`,
    });

    try {
      const ticket = await api.get(`/support_tickets/${parsedId}`);
      if (ticket && ticket.raised_by) {
        await api.post('/notifications', {
          user_id: ticket.raised_by,
          title: "Support Ticket Updated",
          message: `An admin has responded to your ticket #${ticket.id}: "${ticket.title}"`,
          is_read: false,
          created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
        });
      }
    } catch (err) {
      console.warn("Failed to create notification for ticket response", err);
    }
    
    return response;
  }
};
