import { api } from '../../api';

export const clubsApi = {
  getAllClubs: async (params = {}) => {
    const res = await api.get('/clubs', { params });
    return res;
  },

  getClubById: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}`);
    return res;
  },
  getClubEvents: async (clubId) => {
    const response = await api.get(
        `/events?club_id=${clubId}`
    );
    
    return response;
  },
  updateEvent: async (eventId, eventData, userId) => {
    const res = await api.patch(
      `/events/${eventId}`,
      eventData,
      {
        headers: {
          "X-User-Id": userId
        }
      }
    );
    return res;
  },
  getClubRecentActivity: async (clubId) => {
    return [];
  },
  getClubCommittees: async (clubId) => {
    const committees = await api.get(`/clubs/${clubId}/committees`);
    return committees;
  },
  createCommittee: async (clubId, payload, createdBy) => {
    const res = await api.post(`/clubs/${clubId}/committees`, payload);
    return res;
  },
  getUserCertificates: async (userId) => {
    return await api.get(`/users/${userId}/certificates`);
  },
  getCommitteeMembers: async (committeeId) => {
    const members = await api.get(`/committees/${committeeId}/members`);
    if (Array.isArray(members)) {
      return members.map(m => ({
        ...m.committee_membership,
        user: m.user,
        membership: m.membership
      }));
    }
    return members;
  },
  addCommitteeMember: async (committeeId, membershipId, role = 'member') => {
    return await api.post(`/committees/${committeeId}/members`, { membership_id: membershipId, role });
  },
  removeCommitteeMember: async (committeeMembershipId) => {
    return await api.del(`/committee-memberships/${committeeMembershipId}`);
  },
  updateCommitteeMemberRole: async (committeeMembershipId, role) => {
    return await api.patch(`/committee-memberships/${committeeMembershipId}`, { role });
  },
  getUserClubs: async (userId) => {
    const res = await api.get(`/users/${userId}/clubs`);
    return res;
  },
  requestJoinCommittee: async (committeeId, userId) => {
    // For now, mock this since backend doesn't have an endpoint for committee requests
    return new Promise(resolve => setTimeout(resolve, 500));
  },
  getCommitteeTasks: async (clubId, committeeId) => {
    const res = await api.get(
      `/clubs/${clubId}/tasks?committee_id=${committeeId}`
    );
    return res;
  },
  getUserRoleInClub: async (userId, clubId) => {
    const res = await api.get(`/clubs/${clubId}/members/${userId}/role`);
    return res?.role_in_club || null;
  },
  getClubAnalytics: async (clubId) => {
    // Note: This matches the mock implementation for now until a dedicated backend endpoint is built.
    const membersRes = await api.get(`/clubs/${clubId}/members`).catch(() => ({ data: [] }));
    const eventsRes = await api.get(`/events?club_id=${clubId}`).catch(() => ({ data: [] }));
    const tasksRes = await api.get(`/clubs/${clubId}/tasks`).catch(() => ({ data: [] }));
    const budgetsRes = await api.get(`/budgets?club_id=${clubId}`).catch(() => ({ data: [] }));
    const expensesRes = await api.get(`/expenses?club_id=${clubId}`).catch(() => ({ data: [] }));

    const members = membersRes.data || membersRes || [];
    const events = eventsRes.data || eventsRes || [];
    const tasks = tasksRes.data || tasksRes || [];
    const budgets = budgetsRes.data || budgetsRes || [];
    const expenses = expensesRes.data || expensesRes || [];
    
    // Generate 6-month membership growth timeline
    const membershipGrowth = [];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    let cumulative = Math.max(1, members.length - 12);
    months.forEach(month => {
      cumulative += Math.floor(Math.random() * 2);
      membershipGrowth.push({ month, members: cumulative });
    });
    if (membershipGrowth.length > 0) {
      membershipGrowth[membershipGrowth.length - 1].members = members.length;
    }

    // Fetch attendance and registrations for the first 6 events
    const topEvents = events.slice(0, 6);
    const eventAttendance = await Promise.all(topEvents.map(async (e) => {
      const eId = String(e.id);
      const regRes = await api.get(`/events/${eId}/register`).catch(() => ({ data: [] }));
      const attRes = await api.get(`/events/${eId}/attendance`).catch(() => ({ data: [] }));
      const regs = regRes.data || regRes || [];
      const atts = attRes.data || attRes || [];
      
      return {
        name: e.title?.substring(0, 15) || 'Event',
        registered: Math.max(regs.length, 0),
        attended: Math.max(atts.filter(a => a.status === 'present').length, 0)
      };
    }));

    // Budget utilization
    const totalAllocated = budgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount || 0), 0);
    const totalSpent = expenses.filter(e => (e.status || '').toLowerCase() === 'approved').reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
    
    // Expense breakdown by category
    const expenseByCategory = {};
    expenses.filter(e => (e.status || '').toLowerCase() === 'approved').forEach(e => {
      const cat = e.category || 'Other';
      expenseByCategory[cat] = (expenseByCategory[cat] || 0) + parseFloat(e.amount || 0);
    });
    const expenseDistribution = Object.entries(expenseByCategory).map(([name, value]) => ({ name, value: Math.round(value) }));
    const remaining = totalAllocated - totalSpent;
    if (remaining > 0) {
       expenseDistribution.push({ name: 'Remaining', value: Math.round(remaining) });
    }

    // Task completion tracking
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const taskCompletionRate = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 100;
    
    const taskStats = [
      { name: 'Completed', value: completedTasks },
      { name: 'In Progress', value: tasks.filter(t => t.status === 'in_progress').length },
      { name: 'Pending Review', value: tasks.filter(t => t.status === 'pending_review').length },
      { name: 'Overdue', value: tasks.filter(t => t.status === 'missed' || t.status === 'overdue').length }
    ].filter(s => s.value > 0);

    // Timeline of task completions (mocking last 7 days)
    const taskTrend = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      taskTrend.push({
        date: d.toLocaleDateString('en-US', { weekday: 'short' }),
        completed: Math.floor(Math.random() * 5),
        assigned: Math.floor(Math.random() * 5) + 1
      });
    }

    return {
      summary: {
        totalMembers: members.length,
        totalEvents: events.length,
        taskCompletionRate,
        totalTasks: tasks.length
      },
      membershipGrowth,
      eventAttendance,
      expenseDistribution,
      taskStats,
      taskTrend,
      budgetUtilization: {
        total: totalAllocated,
        spent: totalSpent,
        percentage: totalAllocated > 0 ? Math.min(100, Math.round((totalSpent / totalAllocated) * 100)) : 0
      }
    };
  },

  getClubMembers: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/members`);
    return res;
  },

  getMembershipRequests: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/membership-requests`);
    return res;
  },

  joinClub: async (clubId, userId, role = 'member', reason = '') => {
    const res = await api.post(`/clubs/${clubId}/join`, {
      role_in_club: role,
      reason: reason
    });
    return res;
  },

  approveMembership: async (membershipId, approvedBy) => {
    const res = await api.patch(`/memberships/${membershipId}/approve`);
    return res;
  },

  rejectMembership: async (membershipId, rejectedBy, reason = '') => {
    const res = await api.patch(`/memberships/${membershipId}/reject`, { reason });
    return res;
  },

  updateMemberRole: async (clubId, membershipId, newRole, changedBy) => {
    const res = await api.patch(`/clubs/${clubId}/memberships/${membershipId}/role`, { role_in_club: newRole });
    console.log(res);
    return res;
  },

  removeMember: async (clubId, membershipId, removedBy) => {
    const res = await api.(`/clubs/${clubId}/memberships/${membershipId}`);
    return res;
  },

  leaveClub: async (membershipId, userId) => {
    const res = await api.post(`/memberships/${membershipId}/leave`);
    return res;
  },

  // ── Volunteer Tasks ──

  getMyTasks: async (clubId, userId) => {
    const res = await api.get(`/clubs/${clubId}/tasks?user_id=${userId}`);
    return res;
  },

  getClubTasks: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/tasks`);
    return res;
  },

  createTask: async (eventId, assigneeMembershipId, assignedBy, description, dueAt, committeeId = null) => {
    const res = await api.post('/volunteer-tasks', {
      event_id: eventId,
      assignee_membership_id: assigneeMembershipId,
      task_description: description,
      due_at: dueAt,
      committee_id: committeeId
    });
    return res;
  },
  updateTask: async (taskId, updates, currentUserId) => {
    const res = await api.patch(`/volunteer-tasks/${taskId}`, updates);
    return res;
  },

  updateTaskStatus: async (taskId, newStatus, userId) => {
    const res = await api.patch(`/volunteer-tasks/${taskId}/status`, { status: newStatus });
    return res;
  },

  checkOverdueTasks: async () => {
    const res = await api.post('/volunteer-tasks/check-overdue');
    return res;
  },

  // ── Announcements ──

  getClubAnnouncements: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/announcements`);
    return res;
  },

  // ── Club Settings ──

  updateClubSettings: async (clubId, updates, userId) => {
    const res = await api.patch(`/clubs/${clubId}/settings`, updates);
    return res;
  },

  // ── Club Applications (New Workflow) ──

  submitJoinApplication: async (clubId, userId, applicationData) => {
    const res = await api.post(`/clubs/${clubId}/applications`, { ...applicationData, user_id: userId });
    return res;
  },

  getClubApplications: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/applications`);
    return res;
  },

  reviewApplication: async (applicationId, decision, reviewerId, reviewComments = '') => {
    const res = await api.patch(`/club-applications/${applicationId}/review`, {
      decision,
      reviewer_id: reviewerId,
      review_comments: reviewComments
    });
    return res;
  },

  getUserApplications: async (userId) => {
    const res = await api.get(`/users/${userId}/club-applications`);
    return res;
  },

  // ── Club Interests ──

  getClubInterests: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/interests`);
    return res;
  },

  setClubInterests: async (clubId, interestIds) => {
    const res = await api.post(`/clubs/${clubId}/interests`, { interests: interestIds });
    return res;
  },

  // ── Club Creation Workflow (Phase 2) ──

  getClubCreationRequests: async () => {
    const res = await api.get('/club-creation-requests');
    return res;
  },

  getFacultyClubRequests: async (facultyAdvisorId) => {
    const res = await api.get(`/club-creation-requests?faculty_advisor_id=${facultyAdvisorId}`);
    return res;
  },

  requestClubCreation: async (requesterId, clubData) => {
    const res = await api.post('/club-creation-requests', {
      requester_id: requesterId,
      ...clubData
    });
    return res;
  },

  approveClubRequest: async (requestId, adminId) => {
    const res = await api.patch(`/club-creation-requests/${requestId}/approve`, { admin_id: adminId });
    return res;
  },

  rejectClubRequest: async (requestId, rejectorId) => {
    const res = await api.patch(`/club-creation-requests/${requestId}/reject`, { rejector_id: rejectorId });
    return res;
  },

  // ── Create Event ──

  createEvent: async (eventData, clubId) => {
    const res = await api.post('/events', {
      ...eventData,
      club_id: clubId,
    });
    return res;
  },
  // ===============================
  // Club Resources
  // ===============================

  getClubResources: async (clubId) => {
    const res = await api.get(`/clubs/${clubId}/resources`);
    return res;
  },

  addClubResource: async (clubId, resourceData) => {
    const res = await api.post(
      `/clubs/${clubId}/resources`,
      resourceData
    );
    return res;
  },

  ClubResource: async (clubId, resourceId) => {
    const res = await api.del(
      `/clubs/${clubId}/resources/${resourceId}`
    );
    return res;
  },

  // ===============================
  // Committee Resources
  // ===============================

  getCommitteeResources: async (committeeId) => {
    const res = await api.get(
      `/committees/${committeeId}/resources`
    );
    return res;
  },
  addCommitteeResource: async (committeeId, resourceData) => {
    const res = await api.post(
      `/committees/${committeeId}/resources`,
      resourceData
    );
    return res;
  },
  deleteCommitteeResource: async (committeeId, resourceId) => {
    const res = await api.del(
      `/committees/${committeeId}/resources/${resourceId}`
    );
    return res;
  },
  // ── Budgets ─────────────────────────────

  getClubBudgets: async (clubId) => {
    const res = await api.get(`/budgets?club_id=${clubId}`);
    return res;
  },

  getCommitteeBudgets: async (clubId, committeeId) => {
    // If you still need committee budgets, filter on backend or client.
    // Simple approach: fetch all budgets for the club and filter by committee_id.
    const budgets = await api.get(`/budgets?club_id=${clubId}`);
    return budgets.filter(b => String(b.committee_id) === String(committeeId));
  },

  allocateCommitteeBudget: async (clubId, committeeId, budgetData) => {
    // Add committee_id into the payload; URL stays flat.
    const res = await api.post(`/budgets`, {
      ...budgetData,
      club_id: clubId,
      committee_id: committeeId,
    });
    return res;
  },

  // ── Expenses ─────────────────────────────

  getClubExpenses: async (clubId) => {
    const budgets = await api.get(`/budgets?club_id=${clubId}`);

    const allExpenses = await Promise.all(
      budgets.map(b => api.get(`/expenses?budget_id=${b.id}`))
    );

    return allExpenses.flat();
  },

  createExpense: async (expenseData) => {
    const res = await api.post(`/expenses`, expenseData);
    return res;
  },

  approveExpense: async (expenseId, approvedBy, userRole) => {
    const res = await api.patch(
      `/expenses/${expenseId}`,
      { status: 'approved', approval_status: 'approved', approved_by: approvedBy }
    );
    return res;
  },
  transferPresidency: async (clubId, currentMembershipId, successorMembershipId) => {
    const res = await api.patch(
      `/clubs/${clubId}/transfer-presidency`,
      {
        current_membership_id: currentMembershipId,
        successor_membership_id: successorMembershipId,
      }
    );
    return res;
  },
  
};
