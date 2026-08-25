import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

const toId = (id) => (/^\d+$/.test(String(id)) ? parseInt(id, 10) : id);

const getAdvisedClubIds = async (userId) => {
  const clubs = await api.get(`/clubs?faculty_advisor_id=${toId(userId)}`);
  return clubs.map((c) => toId(c.id));
};

const notify = (userId, title, body) =>
  api.post('/notifications', {
    user_id: toId(userId),
    title,
    body,
    is_read: 0,
    created_at: new Date().toISOString(),
  });

export const facultyAdvisorApi = {
  getStats: async (userId) => {
    const clubIds = await getAdvisedClubIds(userId);
    const [clubs, events, budgets] = await Promise.all([
      api.get(`/clubs?faculty_advisor_id=${toId(userId)}`),
      Promise.all(clubIds.map((id) => api.get(`/events?club_id=${id}`))).then((r) => r.flat()),
      Promise.all(clubIds.map((id) => api.get(`/budgets?club_id=${id}`))).then((r) => r.flat()),
    ]);

    const budgetIds = budgets.map((b) => toId(b.id));
    const expenses = (
      await Promise.all(budgetIds.map((id) => api.get(`/expenses?budget_id=${id}`)))
    ).flat();

    return {
      advisedClubs: clubs.length,
      totalMembers: clubs.reduce((sum, c) => sum + (c.member_count_cache || 0), 0),
      pendingEvents: events.filter((e) => e.approval_status === 'pending').length,
      pendingExpenses: expenses.filter((e) => e.approval_status === 'pending').length,
    };
  },

  getAdvisedClubs: async (userId) => api.get(`/clubs?faculty_advisor_id=${toId(userId)}`),

  getClubDetail: async (clubId) => {
    const [club, memberships, committees, budgets] = await Promise.all([
      api.get(`/clubs/${toId(clubId)}`),
      api.get(`/club_memberships?club_id=${toId(clubId)}&status=approved`),
      api.get(`/committees?club_id=${toId(clubId)}`),
      api.get(`/budgets?club_id=${toId(clubId)}`)
    ]);

    const users = await api.get('/users');
    const membersWithNames = memberships.map((m) => ({
      ...m,
      user_name: users.find((u) => toId(u.id) === toId(m.user_id))?.full_name || 'Unknown',
    }));

    const mainBudget = budgets.find(b => !b.committee_id && !b.parent_budget_id) || null;

    return { ...club, members: membersWithNames, committees, mainBudget };
  },

  getEvents: async (userId, status) => {
    const clubIds = await getAdvisedClubIds(userId);
    const clubs = await api.get(`/clubs?faculty_advisor_id=${toId(userId)}`);
    const events = (
      await Promise.all(clubIds.map((id) => api.get(`/events?club_id=${id}`)))
    ).flat();

    const withClubName = events.map((e) => ({
      ...e,
      club_name: clubs.find((c) => toId(c.id) === toId(e.club_id))?.name || 'Unknown',
    }));

    return status ? withClubName.filter((e) => e.approval_status === status) : withClubName;
  },

  decideEvent: async (eventId, { approval_status, review_comments, reviewed_by }) => {
    const updated = await api.patch(`/events/${toId(eventId)}`, {
      approval_status,
      review_comments,
      reviewed_by: toId(reviewed_by),
    });
    await notify(
      updated.created_by,
      `Event ${approval_status === 'approved' ? 'Approved' : 'Rejected'}`,
      `Your event "${updated.title}" was ${approval_status} by your faculty advisor.`
    );
    
    await logAudit({
      userId: toId(reviewed_by),
      action: 'UPDATE',
      entityType: 'Event',
      entityId: toId(eventId),
      details: `Faculty Advisor ${approval_status} Event #${eventId}`,
    });
    
    return updated;
  },

  getExpenses: async (userId, status) => {
    const clubIds = await getAdvisedClubIds(userId);
    const budgets = (
      await Promise.all(clubIds.map((id) => api.get(`/budgets?club_id=${id}`)))
    ).flat();
    const expenses = (
      await Promise.all(budgets.map((b) => api.get(`/expenses?budget_id=${toId(b.id)}`)))
    ).flat();

    const withBudgetTitle = expenses.map((e) => ({
      ...e,
      budget_title: budgets.find((b) => toId(b.id) === toId(e.budget_id))?.title || 'Unknown',
    }));

    return status ? withBudgetTitle.filter((e) => e.approval_status === status) : withBudgetTitle;
  },

  decideExpense: async (expenseId, { approval_status, approval_remarks, approved_by }) => {
    const updated = await api.patch(`/expenses/${toId(expenseId)}`, {
      approval_status,
      status: approval_status,
      approval_remarks,
      approved_by: toId(approved_by),
      approval_date: istNow(),
    });
    await notify(
      updated.submitted_by,
      `Expense ${approval_status === 'approved' ? 'Approved' : 'Rejected'}`,
      `Your expense "${updated.description}" was ${approval_status}.`
    );
    
    await logAudit({
      userId: toId(approved_by),
      action: 'UPDATE',
      entityType: 'Expense',
      entityId: toId(expenseId),
      details: `Faculty Advisor ${approval_status} Expense #${expenseId}`,
    });
    
    return updated;
  },

  getAnnouncements: async (userId) => {
    const clubIds = await getAdvisedClubIds(userId);
    const clubs = await api.get(`/clubs?faculty_advisor_id=${toId(userId)}`);
    const perClub = await Promise.all(clubIds.map((id) => api.get(`/announcements?club_id=${id}`)));
    const flat = perClub.flat().map((a) => ({
      ...a,
      club_name: clubs.find((c) => toId(c.id) === toId(a.club_id))?.name || 'Unknown',
    }));
    return flat.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  postAnnouncement: async ({ club_id, posted_by, title, body, target_audience }) => {
    const payload = {
      club_id: toId(club_id),
      posted_by: toId(posted_by),
      title,
      body,
      target_audience: target_audience || 'all_members',
      created_at: istNow(),
    };
    const created = await api.post('/announcements', payload);
    
    await logAudit({
      userId: toId(posted_by),
      action: 'CREATE',
      entityType: 'Announcement',
      entityId: created.id,
      details: `Faculty Advisor posted announcement: ${title}`,
    });
    
    return created;
  },

  setClubBudget: async (clubId, amount, facultyId) => {
    console.log('[setClubBudget] called with', { clubId, amount, facultyId });

    const parsedClubId = toId(clubId);
    const parsedFacultyId = toId(facultyId);
    const parsedAmount = parseFloat(amount);

    if (!parsedClubId || !parsedFacultyId || Number.isNaN(parsedAmount)) {
      const err = new Error('Invalid arguments to setClubBudget');
      console.error('[setClubBudget] invalid args', { parsedClubId, parsedFacultyId, parsedAmount });
      throw err;
    }

    console.log('[setClubBudget] fetching budgets for club', parsedClubId);
    const budgets = await api.get(`/budgets?club_id=${parsedClubId}`);
    console.log('[setClubBudget] budgets response', budgets);

    const mainBudget = budgets.find(b => !b.committee_id && !b.parent_budget_id);

    if (mainBudget) {
      console.log('[setClubBudget] updating existing mainBudget', mainBudget.id);
      const updated = await api.patch(`/budgets/${mainBudget.id}`, {
        allocated_amount: parsedAmount,
        updated_at: istNow()
      });
      console.log('[setClubBudget] update response', updated);

      await logAudit({
        userId: parsedFacultyId,
        action: 'UPDATE',
        entityType: 'Budget',
        entityId: mainBudget.id,
        details: `Faculty Advisor updated club budget to ${amount}`,
      });

      return updated;
    } else {
      console.log('[setClubBudget] creating new main budget for club', parsedClubId);
      const created = await api.post('/budgets', {
        club_id: parsedClubId,
        title: 'Main Club Budget',
        allocated_amount: parsedAmount,
        status: 'approved',
        created_by: parsedFacultyId,
        created_at: istNow(),
        period_start: istNow(),
        period_end: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString()
      });
      console.log('[setClubBudget] create response', created);

      await logAudit({
        userId: parsedFacultyId,
        action: 'CREATE',
        entityType: 'Budget',
        entityId: created.id,
        details: `Faculty Advisor created club budget: ${amount}`,
      });

      return created;
    }
  }
};
