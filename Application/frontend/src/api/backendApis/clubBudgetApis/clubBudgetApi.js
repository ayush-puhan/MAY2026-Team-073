// clubBudgetApi.js
import { api } from '../../api';

const toId = (id) => (/^\d+$/.test(String(id)) ? parseInt(id, 10) : id);

const istNow = () => new Date().toISOString();

export const clubBudgetApi = {
  setClubBudget: async (clubId, amount, facultyId) => {
    const parsedClubId = toId(clubId);
    const parsedFacultyId = toId(facultyId);
    const parsedAmount = parseFloat(amount);

    // 1. check if a main budget exists
    const budgets = await api.get(`/budgets?club_id=${parsedClubId}`);
    const mainBudget = budgets.find(
      (b) => !b.committee_id && !b.parent_budget_id
    );

    if (mainBudget) {
      // update
      const updated = await api.patch(`/budgets/${mainBudget.id}`, {
        allocated_amount: parsedAmount,
        updated_at: istNow(),
      });

      return updated;
    } else {
      // create
      const created = await api.post('/budgets', {
        club_id: parsedClubId,
        title: 'Main Club Budget',
        allocated_amount: parsedAmount,
        status: 'approved',
        created_by: parsedFacultyId,
        created_at: istNow(),
        period_start: istNow(),
        period_end: new Date(
          new Date().setFullYear(new Date().getFullYear() + 1)
        ).toISOString(),
      });

      return created;
    }
  },
};
