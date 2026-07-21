import { api } from '../../api';

export const rewardsRealApi = {
  getRewardTasks: async () => {
    return await api.get('/rewards/tasks');
  },
  getTaskCompletions: async (userId) => {
    return await api.get(`/rewards/tasks/completions/${userId}`);
  },
  completeTask: async (userId, taskId) => {
    return await api.post('/rewards/tasks/complete', { user_id: userId, task_id: taskId });
  },
  getUserPoints: async (userId) => {
    const res = await api.get(`/rewards/points/${userId}`);
    return res.balance;
  },
  getPointsHistory: async (userId) => {
    return await api.get(`/rewards/ledger/${userId}`);
  },
  getStoreItems: async () => {
    return await api.get('/rewards/store/items');
  },
  redeemItem: async (userId, itemId) => {
    return await api.post('/rewards/store/redeem', { user_id: userId, item_id: itemId });
  },
  getRedemptionHistory: async (userId) => {
    return await api.get(`/rewards/redemptions/${userId}`);
  }
};
