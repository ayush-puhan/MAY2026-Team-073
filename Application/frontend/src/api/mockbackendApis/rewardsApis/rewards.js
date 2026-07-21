import { api } from '../../api';

export const rewardsMockApi = {
  getRewardTasks: async () => {
    return await api.get('/reward_tasks');
  },
  getTaskCompletions: async (userId) => {
    const completions = await api.get('/reward_task_completions');
    return completions.filter(c => c.user_id === userId);
  },
  completeTask: async (userId, taskId) => {
    // Check if task exists and is active
    const tasks = await api.get('/reward_tasks');
    const task = tasks.find(t => t.id === Number(taskId) || t.id === String(taskId));
    if (!task) throw new Error('Task not found');

    // Enforce max completions
    const completions = await rewardsMockApi.getTaskCompletions(userId);
    const taskCompletions = completions.filter(c => c.task_id === task.id).length;
    if (taskCompletions >= (task.max_completions || 1)) {
      throw new Error('Task completion limit reached');
    }

    // Real Verification Logic
    const taskIdStr = String(task.id);
    
    if (taskIdStr === '4') { // Profile Completion
      const users = await api.get('/users');
      const currentUser = users.find(u => u.id === String(userId) || u.id === Number(userId));
      if (!currentUser) throw new Error('User not found');
      
      const missingFields = [];
      if (!currentUser.profile_photo_url) missingFields.push('Profile Photo');
      if (!currentUser.phone) missingFields.push('Phone Number');
      if (!currentUser.dob) missingFields.push('Date of Birth');
      
      if (missingFields.length > 0) {
        throw new Error(`Profile incomplete. Missing: ${missingFields.join(', ')}`);
      }
    }
    else if (taskIdStr === '2') { // Attend 3 Club Events
      const regs = await api.get('/event_registrations');
      const userRegs = regs.filter(r => r.user_id === String(userId) || r.user_id === Number(userId));
      if (userRegs.length < 3) {
        throw new Error(`You have only attended ${userRegs.length} out of 3 required events.`);
      }
    }
    else if (taskIdStr === '6') { // RSVP to a Workshop
      const regs = await api.get('/event_registrations');
      const userRegs = regs.filter(r => r.user_id === String(userId) || r.user_id === Number(userId));
      if (userRegs.length === 0) {
        throw new Error('You have not RSVP\'d to any events yet.');
      }
    }
    else if (taskIdStr === '7') { // Join a New Club
      const memberships = await api.get('/club_memberships');
      const userClubs = memberships.filter(m => m.user_id === String(userId) || m.user_id === Number(userId));
      if (userClubs.length === 0) {
        throw new Error('You are not a member of any clubs yet. Join one first!');
      }
    }
    else if (taskIdStr === '10') { // Easter Egg
      throw new Error('Nice try! You must find the actual easter egg hidden somewhere else in the app.');
    }

    // Create completion record
    const completion = await api.post('/reward_task_completions', {
      user_id: userId,
      task_id: task.id,
      completed_at: new Date().toISOString()
    });

    // Add points to ledger
    await api.post('/reward_points_ledger', {
      user_id: userId,
      points: task.points,
      reason: task.title,
      source_event_id: null,
      created_at: new Date().toISOString()
    });

    return completion;
  },
  getUserPoints: async (userId) => {
    const ledger = await api.get('/reward_points_ledger');
    const userLedger = ledger.filter(l => l.user_id === userId);
    const earned = userLedger.reduce((sum, r) => sum + r.points, 0);

    const redemptions = await api.get('/reward_redemptions');
    const userRedemptions = redemptions.filter(r => r.user_id === userId);
    const spent = userRedemptions.reduce((sum, r) => sum + r.points_spent, 0);

    return earned - spent;
  },
  getPointsHistory: async (userId) => {
    const ledger = await api.get('/reward_points_ledger');
    return ledger.filter(l => l.user_id === userId);
  },
  getStoreItems: async () => {
    return await api.get('/reward_store_items');
  },
  redeemItem: async (userId, itemId) => {
    const items = await api.get('/reward_store_items');
    const item = items.find(i => i.id === Number(itemId) || i.id === String(itemId));
    if (!item) throw new Error('Item not found');

    // Enforce max_per_user
    const redemptions = await rewardsMockApi.getRedemptionHistory(userId);
    const itemRedemptions = redemptions.filter(r => r.reward_description === item.name).length;
    if (itemRedemptions >= (item.max_per_user || 1)) {
      throw new Error(`You have reached the limit of ${item.max_per_user} redemptions for this item.`);
    }

    const currentPoints = await rewardsMockApi.getUserPoints(userId);
    if (currentPoints < item.points_cost) {
      throw new Error('Insufficient points');
    }

    const redemption = await api.post('/reward_redemptions', {
      user_id: userId,
      points_spent: item.points_cost,
      reward_description: item.name,
      status: 'PENDING',
      approved_by: null,
      created_at: new Date().toISOString()
    });

    return redemption;
  },
  getRedemptionHistory: async (userId) => {
    const redemptions = await api.get('/reward_redemptions');
    return redemptions.filter(r => r.user_id === userId);
  }
};
