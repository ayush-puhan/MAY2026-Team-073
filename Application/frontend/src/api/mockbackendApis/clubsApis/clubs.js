import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

// Lazy-import notificationApi to avoid circular deps
const getNotificationApi = async () => {
  const mod = await import('../notificationApis/notification');
  return mod.notificationApi;
};

export const clubsApi = {
  // ── Read Operations ──

  getAllClubs: async (universityId = null) => {
    const [clubs, universities, clubInterests, interests, allMemberships, allUsers] = await Promise.all([
      api.get('/clubs'),
      api.get('/universities'),
      api.get('/club_interests'),
      api.get('/interests'),
      api.get('/club_memberships?status=approved'),
      api.get('/users')
    ]);
    
    let filteredClubs = clubs;
    if (universityId) {
      filteredClubs = clubs.filter(c => String(c.university_id) === String(universityId));
    }

    return filteredClubs.map(c => {
      // Find interests for this club
      const cInterests = clubInterests.filter(ci => String(ci.club_id) === String(c.id));
      const interestNames = cInterests.map(ci => {
        const found = interests.find(i => String(i.id) === String(ci.interest_id));
        return found ? found.name : null;
      }).filter(Boolean);

      // Calculate student members
      const clubMembers = allMemberships.filter(m => String(m.club_id) === String(c.id));
      const studentMembersCount = clubMembers.reduce((count, m) => {
        const u = allUsers.find(user => String(user.id) === String(m.user_id));
        if (u && u.role === 'student') return count + 1;
        return count;
      }, 0);

      return {
        ...c,
        interests: interestNames,
        university: universities.find(u => String(u.id) === String(c.university_id)),
        members: studentMembersCount
      };
    });
  },

  getClubById: async (clubId) => {
    const [club, universities, clubMemberships, allUsers] = await Promise.all([
      api.get(`/clubs/${clubId}`),
      api.get('/universities'),
      api.get(`/club_memberships?club_id=${clubId}&status=approved`),
      api.get('/users')
    ]);
    if (!club) return null;

    const studentMembersCount = clubMemberships.reduce((count, m) => {
      const u = allUsers.find(user => String(user.id) === String(m.user_id));
      if (u && u.role === 'student') return count + 1;
      return count;
    }, 0);

    return {
      ...club,
      university: universities.find(u => String(u.id) === String(club.university_id)),
      members: studentMembersCount
    };
  },

  getUserClubs: async (userId) => {
    const memberships = await api.get(`/club_memberships?user_id=${userId}&status=approved`);
    const clubIds = new Set(memberships.map(m => String(m.club_id)));
    if (clubIds.size === 0) return [];

    const [clubs, universities, allMemberships, allUsers] = await Promise.all([
      api.get('/clubs'),
      api.get('/universities'),
      api.get('/club_memberships?status=approved'),
      api.get('/users')
    ]);
    
    return clubs
      .filter(club => clubIds.has(String(club.id)))
      .map(c => {
        const membership = memberships.find(m => String(m.club_id) === String(c.id));
        const clubMembers = allMemberships.filter(m => String(m.club_id) === String(c.id));
        const studentMembersCount = clubMembers.reduce((count, m) => {
          const u = allUsers.find(user => String(user.id) === String(m.user_id));
          if (u && u.role === 'student') return count + 1;
          return count;
        }, 0);

        return {
          ...c,
          role_in_club: membership?.role_in_club || 'member',
          membership_id: membership?.id,
          university: universities.find(u => String(u.id) === String(c.university_id)),
          members: studentMembersCount
        };
      });
  },

  // ── Role & Membership Queries ──

  getUserRoleInClub: async (userId, clubId) => {
    const memberships = await api.get(`/club_memberships?user_id=${userId}&club_id=${clubId}&status=approved`);
    if (!memberships || memberships.length === 0) return null;
    return memberships[0].role_in_club;
  },

  getClubMembers: async (clubId) => {
    const memberships = await api.get(`/club_memberships?club_id=${clubId}&status=approved`);
    if (!memberships || memberships.length === 0) return [];

    const users = await api.get('/users');
    return memberships
      .map(m => ({
        ...m,
        user: users.find(u => String(u.id) === String(m.user_id)) || { full_name: 'Unknown', email: '', role: 'unknown' }
      }))
      .filter(m => m.user.role === 'student');
  },

  getMembershipRequests: async (clubId) => {
    const memberships = await api.get(`/club_memberships?club_id=${clubId}&status=pending`);
    if (!memberships || memberships.length === 0) return [];

    const users = await api.get('/users');
    return memberships
      .map(m => ({
        ...m,
        user: users.find(u => String(u.id) === String(m.user_id)) || { full_name: 'Unknown', email: '', role: 'unknown' }
      }))
      .filter(m => m.user.role === 'student');
  },

  getPendingMemberships: async (userId) => {
    const memberships = await api.get(`/club_join_applications?user_id=${userId}&status=pending`);
    return memberships || [];
  },

  // ── Membership Actions ──

  joinClub: async (clubId, userId, role = 'member', reason = '') => {
    const existing = await api.get(`/club_memberships?club_id=${clubId}&user_id=${userId}`);
    if (existing && existing.length > 0) {
      throw new Error("You have already applied to or are a member of this club.");
    }

    const payload = {
      user_id: userId,
      club_id: clubId,
      role_in_club: role,
      status: 'pending',
      applied_at: istNow(),
      reason: reason
    };
    const result = await api.post('/club_memberships', payload);

    // Notify club president
    try {
      const notificationApi = await getNotificationApi();
      const allMembers = await api.get(`/club_memberships?club_id=${clubId}&status=approved`);
      const club = await api.get(`/clubs/${clubId}`);
      const leaders = allMembers.filter(m => ['president', 'vice_president'].includes(m.role_in_club));
      
      for (const leader of leaders) {
        await notificationApi.createNotification({
          userId: leader.user_id,
          type: 'MEMBERSHIP_UPDATE',
          title: 'New Membership Request',
          body: `A new membership request has been submitted for ${club.name}.`,
          channel: 'BOTH',
          relatedEntityType: 'ClubMembership',
          relatedEntityId: result.id
        });
      }
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId,
      action: 'CREATE',
      entityType: 'ClubMembership',
      entityId: result.id,
      details: `User #${userId} requested to join Club #${clubId}`
    });

    return result;
  },

  approveMembership: async (membershipId, approvedBy) => {
    const membership = await api.get(`/club_memberships/${membershipId}`);
    if (!membership) throw new Error('Membership not found');

    await api.patch(`/club_memberships/${membershipId}`, {
      status: 'approved',
      decided_at: istNow(),
      approved_by: approvedBy
    });

    // Send notification + email to applicant
    try {
      const notificationApi = await getNotificationApi();
      const club = await api.get(`/clubs/${membership.club_id}`);
      
      await notificationApi.createNotification({
        userId: membership.user_id,
        type: 'MEMBERSHIP_UPDATE',
        title: 'Membership Approved! 🎉',
        body: `Your application to join ${club.name} has been approved. Welcome aboard!`,
        channel: 'IN_APP',
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });

      const user = await api.get(`/users/${membership.user_id}`);
      await notificationApi.sendEmail(membership.user_id, 'MEMBERSHIP_UPDATE', {
        subject: `Welcome to ${club.name}!`,
        body: `Hi ${user.full_name},\n\nGreat news! Your application to join ${club.name} has been approved.\n\nYou can now access all club resources and participate in upcoming events.\n\nWelcome to the team!`,
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId: approvedBy,
      action: 'UPDATE',
      entityType: 'ClubMembership',
      entityId: membershipId,
      details: `Approved membership #${membershipId}`
    });

    return { success: true };
  },

  rejectMembership: async (membershipId, rejectedBy, reason = '') => {
    const membership = await api.get(`/club_memberships/${membershipId}`);
    if (!membership) throw new Error('Membership not found');

    await api.patch(`/club_memberships/${membershipId}`, {
      status: 'rejected',
      decided_at: istNow(),
      approved_by: rejectedBy,
      rejection_reason: reason
    });

    // Send notification + email to applicant
    try {
      const notificationApi = await getNotificationApi();
      const club = await api.get(`/clubs/${membership.club_id}`);

      await notificationApi.createNotification({
        userId: membership.user_id,
        type: 'MEMBERSHIP_UPDATE',
        title: 'Application Update',
        body: `Your application to join ${club.name} was not approved.${reason ? ` Reason: ${reason}` : ''}`,
        channel: 'IN_APP',
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });

      const user = await api.get(`/users/${membership.user_id}`);
      await notificationApi.sendEmail(membership.user_id, 'MEMBERSHIP_UPDATE', {
        subject: `Update on your ${club.name} application`,
        body: `Hi ${user.full_name},\n\nWe regret to inform you that your application to join ${club.name} was not approved at this time.${reason ? `\n\nReason: ${reason}` : ''}\n\nYou may reapply in the future.`,
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId: rejectedBy,
      action: 'UPDATE',
      entityType: 'ClubMembership',
      entityId: membershipId,
      details: `Rejected membership #${membershipId}. Reason: ${reason}`
    });

    return { success: true };
  },

  // ── Club Applications (New Workflow) ──

  submitJoinApplication: async (clubId, userId, applicationData) => {
    const { interests, ...data } = applicationData;
    
    const payload = {
      ...data,
      user_id: userId,
      club_id: clubId,
      status: 'pending',
      applied_at: istNow()
    };
    
    const result = await api.post('/club_join_applications', payload);
    
    if (interests && interests.length > 0) {
      for (const interestId of interests) {
        await api.post('/application_interests', {
          application_id: result.id,
          interest_id: interestId
        });
      }
    }

    await logAudit({
      userId,
      action: 'CREATE',
      entityType: 'ClubJoinApplication',
      entityId: result.id,
      details: `User #${userId} applied to join Club #${clubId}`
    });

    return result;
  },

  getClubApplications: async (clubId) => {
    const [applications, users, allInterests, appInterests] = await Promise.all([
      api.get(`/club_join_applications?club_id=${clubId}&status=pending`),
      api.get('/users'),
      api.get('/interests'),
      api.get('/application_interests')
    ]);

    if (!applications) return [];

    return applications
      .map(app => {
        const user = users.find(u => String(u.id) === String(app.user_id));
        const myAppInterests = appInterests.filter(ai => String(ai.application_id) === String(app.id));
        const interestTags = myAppInterests.map(ai => {
          const found = allInterests.find(i => String(i.id) === String(ai.interest_id));
          return found ? found.name : null;
        }).filter(Boolean);

        return {
          ...app,
          user: user || { full_name: 'Unknown', email: '', role: 'unknown' },
          interests: interestTags
        };
      })
      .filter(app => app.user.role === 'student');
  },

  reviewApplication: async (applicationId, decision, reviewerId, reviewComments = '') => {
    const application = await api.get(`/club_join_applications/${applicationId}`);
    if (!application) throw new Error('Application not found');

    await api.patch(`/club_join_applications/${applicationId}`, {
      status: decision,
      reviewed_by: reviewerId,
      review_comments: reviewComments,
      reviewed_at: istNow()
    });

    if (decision === 'approved') {
      await api.post('/club_memberships', {
        user_id: application.user_id,
        club_id: application.club_id,
        role_in_club: 'member',
        status: 'approved',
        joined_at: istNow()
      });
    }

    await logAudit({
      userId: reviewerId,
      action: 'UPDATE',
      entityType: 'ClubJoinApplication',
      entityId: applicationId,
      details: `Reviewed application #${applicationId}. Decision: ${decision}`
    });

    return { success: true };
  },

  getUserApplications: async (userId) => {
    const [applications, clubs] = await Promise.all([
      api.get(`/club_join_applications?user_id=${userId}`),
      api.get('/clubs')
    ]);

    return (applications || []).map(app => ({
      ...app,
      club: clubs.find(c => String(c.id) === String(app.club_id))
    }));
  },

  // ── Club Interests ──

  getClubInterests: async (clubId) => {
    const [clubInterests, allInterests] = await Promise.all([
      api.get(`/club_interests?club_id=${clubId}`),
      api.get('/interests')
    ]);

    if (!clubInterests) return [];
    
    return clubInterests.map(ci => {
      const interest = allInterests.find(i => String(i.id) === String(ci.interest_id));
      return {
        ...ci,
        interest
      };
    });
  },

  setClubInterests: async (clubId, interestIds) => {
    // Note: mock backend deletes usually need id. We might have to get and delete one by one.
    const existing = await api.get(`/club_interests?club_id=${clubId}`);
    for (const e of existing) {
      await api.delete(`/club_interests/${e.id}`);
    }

    for (const interestId of interestIds) {
      await api.post('/club_interests', {
        club_id: clubId,
        interest_id: interestId,
        created_at: istNow()
      });
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (!user.id) throw new Error("Authentication required. Please log in to perform this action.");
    
    await logAudit({
      userId: user.id,
      action: 'UPDATE',
      entityType: 'Club',
      entityId: clubId,
      details: `Updated club interests for club #${clubId}`
    });
    
    return { success: true };
  },

  updateMemberRole: async (membershipId, newRole, changedBy) => {
    const membership = await api.get(`/club_memberships/${membershipId}`);
    if (!membership) throw new Error('Membership not found');

    const oldRole = membership.role_in_club;
    await api.patch(`/club_memberships/${membershipId}`, { role_in_club: newRole });

    // Notify member of role change
    try {
      const notificationApi = await getNotificationApi();
      const club = await api.get(`/clubs/${membership.club_id}`);

      await notificationApi.createNotification({
        userId: membership.user_id,
        type: 'MEMBERSHIP_UPDATE',
        title: 'Role Updated',
        body: `Your role in ${club.name} has been changed from ${oldRole} to ${newRole}.`,
        channel: 'BOTH',
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId: changedBy,
      action: 'UPDATE',
      entityType: 'ClubMembership',
      entityId: membershipId,
      details: `Changed role from ${oldRole} to ${newRole}`
    });

    return { success: true };
  },

  removeMember: async (membershipId, removedBy) => {
    const membership = await api.get(`/club_memberships/${membershipId}`);
    if (!membership) throw new Error('Membership not found');

    await api.patch(`/club_memberships/${membershipId}`, {
      status: 'withdrawn',
      decided_at: istNow()
    });

    try {
      const notificationApi = await getNotificationApi();
      const club = await api.get(`/clubs/${membership.club_id}`);

      await notificationApi.createNotification({
        userId: membership.user_id,
        type: 'MEMBERSHIP_UPDATE',
        title: 'Membership Update',
        body: `Your membership in ${club.name} has been ended.`,
        channel: 'BOTH',
        relatedEntityType: 'ClubMembership',
        relatedEntityId: membershipId
      });
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId: removedBy,
      action: 'DELETE',
      entityType: 'ClubMembership',
      entityId: membershipId,
      details: `Removed member from club`
    });

    return { success: true };
  },

  leaveClub: async (membershipId, userId) => {
    await api.patch(`/club_memberships/${membershipId}`, {
      status: 'withdrawn',
      decided_at: istNow()
    });

    await logAudit({
      userId,
      action: 'UPDATE',
      entityType: 'ClubMembership',
      entityId: membershipId,
      details: `User left club voluntarily`
    });

    return { success: true };
  },

  // ── Volunteer Tasks ──

  getMyTasks: async (clubId, userId) => {
    // Get user's membership for this club
    const memberships = await api.get(`/club_memberships?user_id=${userId}&club_id=${clubId}&status=approved`);
    if (!memberships || memberships.length === 0) return [];

    const membershipId = memberships[0].id;
    const tasks = await api.get(`/volunteer_assignments?assignee_membership_id=${membershipId}`);
    
    // Enrich with event + assigner data
    const [events, users] = await Promise.all([
      api.get('/events'),
      api.get('/users')
    ]);

    return tasks.map(t => ({
      ...t,
      event: events.find(e => String(e.id) === String(t.event_id)) || { title: 'Unknown Event' },
      assigner: users.find(u => String(u.id) === String(t.assigned_by)) || { full_name: 'Unknown' }
    }));
  },

  getClubTasks: async (clubId) => {
    // Get all events for this club to find its tasks
    const events = await api.get(`/events?club_id=${clubId}`);
    if (!events || events.length === 0) return [];

    const eventIds = new Set(events.map(e => String(e.id)));
    const allTasks = await api.get('/volunteer_assignments');
    const clubTasks = allTasks.filter(t => eventIds.has(String(t.event_id)));

    // Get all memberships and users to populate assignee info
    const [allMemberships, users] = await Promise.all([
      api.get('/club_memberships'),
      api.get('/users')
    ]);

    return clubTasks
      .map(t => {
        const assigneeMembership = allMemberships.find(m => String(m.id) === String(t.assignee_membership_id));
        const assigneeUser = assigneeMembership ? users.find(u => String(u.id) === String(assigneeMembership.user_id)) : null;
        return {
          ...t,
          event: events.find(e => String(e.id) === String(t.event_id)) || { title: 'Unknown Event' },
          assigner: users.find(u => String(u.id) === String(t.assigned_by)) || { full_name: 'Unknown' },
          assignee: assigneeUser || { full_name: 'Unknown' }
        };
      })
      .filter(t => t.assignee && t.assignee.role === 'student');
  },




  createTask: async (eventId, assigneeMembershipId, assignedBy, description, dueAt) => {
    console.log("createTask CALLED WITH:", { eventId, assigneeMembershipId, assignedBy, description, dueAt });
    const result = await api.post('/volunteer_assignments', {
      event_id: eventId,
      assignee_membership_id: assigneeMembershipId,
      assigned_by: assignedBy,
      task_description: description,
      status: 'assigned',
      due_at: dueAt,
      created_at: istNow()
    });

    // Notify assignee
    try {
      const notificationApi = await getNotificationApi();
      const membership = await api.get(`/club_memberships/${assigneeMembershipId}`);

      if (membership) {
        await notificationApi.createNotification({
          userId: membership.user_id,
          type: 'EVENT_REMINDER',
          title: 'New Task Assigned',
          body: `You have been assigned a new task: "${description}"`,
          channel: 'BOTH',
          relatedEntityType: 'VolunteerAssignment',
          relatedEntityId: result.id
        });
      }
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId: assignedBy,
      action: 'CREATE',
      entityType: 'VolunteerAssignment',
      entityId: result.id,
      details: `Task assigned: ${description}`
    });

    return result;
  },

  deleteTask: async (taskId) => {
    return await api.delete(`/volunteer_assignments/${taskId}`);
  },

  updateTask: async (taskId, updates, updatedBy) => {
    const task = await api.get(`/volunteer_assignments/${taskId}`);
    if (!task) throw new Error("Task not found");

    const updatedTask = await api.patch(`/volunteer_assignments/${taskId}`, {
      ...updates,
      updated_at: istNow()
    });

    await logAudit({
      userId: updatedBy,
      action: 'UPDATE',
      entityType: 'VolunteerTask',
      entityId: taskId,
      details: `Updated task: ${taskId}`
    });

    return updatedTask;
  },

  updateTaskStatus: async (taskId, newStatus, userId) => {
    const task = await api.get(`/volunteer_assignments/${taskId}`);
    if (!task) throw new Error('Task not found');

    await api.patch(`/volunteer_assignments/${taskId}`, { status: newStatus });

    try {
      const notificationApi = await getNotificationApi();
      
      // Notify assigner when a task is submitted for review
      if (newStatus === 'pending_review') {
        await notificationApi.createNotification({
          userId: task.assigned_by,
          type: 'EVENT_REMINDER',
          title: 'Task Needs Review',
          body: `A task requires your approval: "${task.task_description}"`,
          channel: 'IN_APP',
          relatedEntityType: 'VolunteerAssignment',
          relatedEntityId: taskId
        });
      }
      
      // Notify assignee if assigner approves (completed) or rejects (in_progress)
      if (newStatus === 'completed') {
        // Need assignee user_id
        const membership = await api.get(`/club_memberships/${task.assignee_membership_id}`);
        if (membership) {
          await notificationApi.createNotification({
            userId: membership.user_id,
            type: 'EVENT_REMINDER',
            title: 'Task Approved',
            body: `Your task has been approved and marked as completed: "${task.task_description}"`,
            channel: 'IN_APP',
            relatedEntityType: 'VolunteerAssignment',
            relatedEntityId: taskId
          });
        }
      } else if (newStatus === 'in_progress' && task.status === 'pending_review') {
        // Rejected back to in_progress
        const membership = await api.get(`/club_memberships/${task.assignee_membership_id}`);
        if (membership) {
          await notificationApi.createNotification({
            userId: membership.user_id,
            type: 'EVENT_REMINDER',
            title: 'Task Changes Requested',
            body: `Your task review was rejected and needs further work: "${task.task_description}"`,
            channel: 'IN_APP',
            relatedEntityType: 'VolunteerAssignment',
            relatedEntityId: taskId
          });
        }
      }
    } catch (e) { console.error('Notification error:', e); }

    await logAudit({
      userId,
      action: 'UPDATE',
      entityType: 'VolunteerAssignment',
      entityId: taskId,
      details: `Task status changed to ${newStatus}`
    });

    return { success: true };
  },

  checkOverdueTasks: async () => {
    const allTasks = await api.get('/volunteer_assignments');
    const now = new Date();
    const overdue = allTasks.filter(t => {
      if (t.status === 'completed' || t.status === 'missed') return false;
      if (!t.due_at) return false;
      return new Date(t.due_at) < now;
    });

    for (const task of overdue) {
      await api.patch(`/volunteer_assignments/${task.id}`, { status: 'missed' });
      
      try {
        const notificationApi = await getNotificationApi();
        const membership = await api.get(`/club_memberships/${task.assignee_membership_id}`);
        
        await notificationApi.createNotification({
          userId: membership.user_id,
          type: 'EVENT_REMINDER',
          title: 'Task Overdue',
          body: `Your task "${task.task_description}" is now overdue and has been marked as missed.`,
          channel: 'BOTH',
          relatedEntityType: 'VolunteerAssignment',
          relatedEntityId: task.id
        });
      } catch (e) { console.error('Notification error:', e); }
    }

    return { markedMissed: overdue.length };
  },

  // ── Announcements ──

  getClubAnnouncements: async (clubId) => {
    const announcements = await api.get(`/announcements?club_id=${clubId}`);
    const users = await api.get('/users');
    return announcements
      .map(a => ({
        ...a,
        poster: users.find(u => String(u.id) === String(a.posted_by)) || { full_name: 'Unknown' }
      }))
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  // ── Club Settings ──

  updateClubSettings: async (clubId, updates, userId) => {
    await api.patch(`/clubs/${clubId}`, updates);

    await logAudit({
      userId,
      action: 'UPDATE',
      entityType: 'Club',
      entityId: clubId,
      details: `Updated club settings: ${Object.keys(updates).join(', ')}`
    });

    return { success: true };
  },

  // ── Club Creation Workflow (Phase 2) ──
  getClubProposals: async () => {
    const requests = await api.get('/club_creation_requests');
    const users = await api.get('/users');
    return requests.map(r => ({
      ...r,
      proposer: users.find(u => String(u.id) === String(r.requester_id)),
      facultyAdvisorEmail: users.find(u => String(u.id) === String(r.faculty_advisor_id))?.email
    }));
  },

  requestClubCreation: async (requesterId, clubData) => {
    // Spam check: ensure user doesn't already have a pending request
    const existingRequests = await api.get(`/club_creation_requests?requester_id=${requesterId}`);
    const hasPending = existingRequests.some(r => ['submitted', 'under_review', 'faculty_recommended'].includes(r.status));
    if (hasPending) {
      throw new Error('You already have a pending club proposal. Please wait for it to be processed before submitting another.');
    }

    // Phase 1 of creation: submit request
    const request = await api.post('/club_creation_requests', {
      requester_id: requesterId,
      proposed_name: clubData.name,
      proposal_description: clubData.description,
      proposed_category: clubData.category,
      proposed_interests: clubData.interests || [],
      faculty_advisor_id: clubData.faculty_advisor_id,
      status: 'submitted', // maps to CLUB_REQUEST_STATUS.SUBMITTED
      created_at: istNow(),
      updated_at: istNow()
    });

    await logAudit({
      userId: requesterId,
      action: 'CREATE',
      entityType: 'ClubCreationRequest',
      entityId: request.id,
      details: `Submitted creation request for club: ${clubData.name}`
    });

    // Notify the selected faculty advisor
    const { notificationApi } = await import('../notificationApis/notification.js');
    await notificationApi.createNotification({
      userId: clubData.faculty_advisor_id,
      type: 'CLUB_PROPOSAL_SUBMITTED',
      title: 'New Club Proposal to Review',
      body: `A student has proposed a new club "${clubData.name}" and requested you as the faculty advisor.`,
      relatedEntityType: 'ClubCreationRequest',
      relatedEntityId: request.id
    });

    return request;
  },

  recommendClubProposal: async (requestId, facultyAdvisorId) => {
    return clubsApi.reviewClubRequest(requestId, facultyAdvisorId, 'faculty_recommended');
  },

  rejectClubProposal: async (requestId, facultyAdvisorId) => {
    return clubsApi.reviewClubRequest(requestId, facultyAdvisorId, 'rejected', 'Faculty advisor declined to sponsor this club.');
  },

  reviewClubRequest: async (requestId, facultyAdvisorId, decision, feedback = '') => {
    // Phase 1 approval: Faculty Advisor review
    // decision should be 'faculty_recommended' (meaning reviewed by faculty, ready for admin) or 'rejected'
    const request = await api.get(`/club_creation_requests/${requestId}`);
    if (!request) throw new Error('Request not found');

    if (String(request.faculty_advisor_id) !== String(facultyAdvisorId)) {
      throw new Error('Only the assigned faculty advisor can review this request');
    }

    const updated = await api.patch(`/club_creation_requests/${requestId}`, {
      status: decision,
      feedback: feedback,
      updated_at: istNow()
    });

    await logAudit({
      userId: facultyAdvisorId,
      action: 'UPDATE',
      entityType: 'ClubCreationRequest',
      entityId: requestId,
      details: `Faculty Advisor reviewed request. Decision: ${decision}`
    });

    const { notificationApi } = await import('../notificationApis/notification.js');
    if (decision === 'faculty_recommended' || decision === 'under_review') {
      // Notify university admins
      const admins = await api.get('/users?role=university_admin');
      for (const admin of admins) {
        await notificationApi.createNotification({
          userId: admin.id,
          type: 'CLUB_PROPOSAL_RECOMMENDED',
          title: 'Faculty Recommended Club Proposal',
          body: `A faculty advisor has recommended the club proposal "${request.proposed_name}" for final admin approval.`,
          relatedEntityType: 'ClubCreationRequest',
          relatedEntityId: request.id
        });
      }
    } else if (decision === 'rejected') {
      // Notify the requester
      await notificationApi.createNotification({
        userId: request.requester_id,
        type: 'CLUB_PROPOSAL_REJECTED',
        title: 'Club Proposal Declined',
        body: `Your club proposal "${request.proposed_name}" was declined by the faculty advisor.`,
        relatedEntityType: 'ClubCreationRequest',
        relatedEntityId: request.id
      });
    }

    return updated;
  },

  approveClubRequest: async (requestId, adminId) => {
    // Phase 2 approval: Admin final approval (Student Welfare / Dean)
    const request = await api.get(`/club_creation_requests/${requestId}`);
    if (!request) throw new Error('Request not found');
    
    if (!['under_review', 'faculty_recommended'].includes(request.status)) {
      throw new Error('Request must be reviewed by faculty advisor first before final approval');
    }

    // 1. Mark request as approved
    await api.patch(`/club_creation_requests/${requestId}`, {
      status: 'approved',
      updated_at: istNow()
    });

    const newClub = await api.post('/clubs', {
      name: request.proposed_name,
      description: request.proposal_description,
      category: request.proposed_category,
      university_id: 1, // Assume IIT Delhi for mock
      status: 'active',
      members: 1, // The requester
      created_at: istNow()
    });

    if (request.proposed_interests && request.proposed_interests.length > 0) {
      await clubsApi.setClubInterests(newClub.id, request.proposed_interests);
    }

    // 3. Make requester the president
    await api.post('/club_memberships', {
      user_id: request.requester_id,
      club_id: newClub.id,
      role_in_club: 'president',
      status: 'approved',
      joined_at: istNow()
    });

    await logAudit({
      userId: adminId,
      action: 'CREATE',
      entityType: 'Club',
      entityId: newClub.id,
      details: `Admin approved creation of club: ${newClub.name}`
    });
    
    // 4. Notify the requester and faculty advisor
    const { notificationApi } = await import('../notificationApis/notification.js');
    await notificationApi.createNotification({
      userId: request.requester_id,
      type: 'CLUB_PROPOSAL_APPROVED',
      title: 'Club Proposal Approved!',
      body: `Congratulations! Your club "${newClub.name}" has been officially approved. You have been assigned as the President.`,
      relatedEntityType: 'Club',
      relatedEntityId: newClub.id
    });
    
    await notificationApi.createNotification({
      userId: request.faculty_advisor_id,
      type: 'CLUB_PROPOSAL_APPROVED',
      title: 'Advised Club Approved',
      body: `The club proposal "${newClub.name}" you recommended has been approved by the admin.`,
      relatedEntityType: 'Club',
      relatedEntityId: newClub.id
    });

    return newClub;
  },

  // ── Phase 2: Events ──

  getClubEvents: async (clubId) => {
    const events = await api.get(`/events?club_id=${clubId}`);
    const clubSponsors = await api.get(`/club_sponsors`) || [];
    const allSponsors = await api.get(`/sponsors`) || [];
    
    // Map sponsors to events
    return events.map(e => {
      const eventSponsorLinks = clubSponsors.filter(cs => String(cs.event_id) === String(e.id));
      const eventSponsors = eventSponsorLinks.map(link => allSponsors.find(s => String(s.id) === String(link.sponsor_id))).filter(Boolean);
      
      // Keep legacy string if it exists, but mapped is better
      return {
        ...e,
        mapped_sponsors: eventSponsors
      };
    });
  },

  createEvent: async (clubId, eventData, creatorId, requiresApproval) => {
    const status = requiresApproval ? 'pending_approval' : 'scheduled';
    const sponsorsInput = eventData.sponsors;
    delete eventData.sponsors;

    const newEvent = await api.post('/events', {
      ...eventData,
      club_id: clubId,
      created_by: creatorId,
      status,
      created_at: istNow(),
      updated_at: istNow()
    });
    
    if (sponsorsInput && typeof sponsorsInput === 'string') {
      const sponsorNames = sponsorsInput.split(',').map(s => s.trim()).filter(s => s);
      for (const name of sponsorNames) {
        const newSponsor = await api.post('/sponsors', {
          organization_name: name,
          contact_email: null,
          contact_person: null,
          created_at: istNow()
        });
        
        await api.post('/club_sponsors', {
          club_id: null,
          event_id: newEvent.id,
          sponsor_id: newSponsor.id,
          sponsorship_details: 'Event Sponsorship'
        });
      }
    }

    if (!requiresApproval) {
      // Notify club members
      try {
        const { notificationApi } = await import('../notificationApis/notification.js');
        const memberships = await api.get(`/club_memberships?club_id=${clubId}&status=approved`);
        const club = await api.get(`/clubs/${clubId}`);
        for (const m of memberships) {
          if (String(m.user_id) !== String(creatorId)) { // don't notify creator
            await notificationApi.createNotification({
              userId: m.user_id,
              type: 'CLUB_UPDATE',
              title: `New Event from ${club.name}`,
              body: `A new event "${eventData.title}" has been scheduled!`,
              channel: 'IN_APP',
              relatedEntityType: 'Event',
              relatedEntityId: newEvent.id
            });
          }
        }
      } catch (e) { console.error('Notification error:', e); }
    }

    await logAudit({
      userId: creatorId,
      action: 'CREATE',
      entityType: 'Event',
      entityId: newEvent.id,
      details: `Created new event: ${eventData.title}`
    });

    return newEvent;
  },

  updateEvent: async (eventId, updates, updatedBy) => {
    const event = await api.get(`/events/${eventId}`);
    if (!event) throw new Error("Event not found");

    const sponsorsInput = updates.sponsors;
    delete updates.sponsors;

    const updatedEvent = await api.patch(`/events/${eventId}`, {
      ...updates,
      updated_at: istNow()
    });

    if (sponsorsInput !== undefined) {
      // Very naive mock update for sponsors - clear existing and re-add
      const existingLinks = await api.get(`/club_sponsors?event_id=${eventId}`);
      if (existingLinks) {
        for (const link of existingLinks) {
          await api.delete(`/club_sponsors/${link.id}`);
        }
      }
      
      if (typeof sponsorsInput === 'string' && sponsorsInput.trim()) {
        const sponsorNames = sponsorsInput.split(',').map(s => s.trim()).filter(s => s);
        for (const name of sponsorNames) {
          const newSponsor = await api.post('/sponsors', {
            organization_name: name,
            contact_email: null,
            contact_person: null,
            created_at: istNow()
          });
          
          await api.post('/club_sponsors', {
            club_id: null,
            event_id: eventId,
            sponsor_id: newSponsor.id,
            sponsorship_details: 'Event Sponsorship'
          });
        }
      }
    }

    return updatedEvent;
  },

  approveEvent: async (eventId, approverId) => {
    await api.patch(`/events/${eventId}`, { status: 'scheduled', updated_at: istNow() });
    
    // Notify club members
    try {
      const { notificationApi } = await import('../notificationApis/notification.js');
      const event = await api.get(`/events/${eventId}`);
      const club = await api.get(`/clubs/${event.club_id}`);
      const memberships = await api.get(`/club_memberships?club_id=${event.club_id}&status=approved`);
      
      for (const m of memberships) {
        await notificationApi.createNotification({
          userId: m.user_id,
          type: 'CLUB_UPDATE',
          title: `New Event from ${club.name}`,
          body: `A new event "${event.title}" has been scheduled!`,
          channel: 'IN_APP',
          relatedEntityType: 'Event',
          relatedEntityId: event.id
        });
      }
    } catch (e) { console.error('Notification error:', e); }

    return { success: true };
  },

  rejectEvent: async (eventId, approverId) => {
    await api.patch(`/events/${eventId}`, { status: 'rejected', updated_at: istNow() });
    return { success: true };
  },

  markAttendance: async (eventId, attendedMembershipIds) => {
    // In a real app this would insert rows into `attendance_records` table.
    // Here we'll mock by patching the event with a field (if we were storing it there) or a new mock endpoint.
    return { success: true };
  },

  // ── Phase 2: Committees ──
  getClubCommittees: async (clubId) => {
    return await api.get(`/committees?club_id=${clubId}`);
  },

  createCommittee: async (clubId, committeeData, creatorId) => {
    return await api.post('/committees', {
      ...committeeData,
      club_id: clubId,
      created_at: istNow()
    });
  },

  getCommitteeMembers: async (committeeId) => {
    const committeeMembers = await api.get(`/committee_memberships?committee_id=${committeeId}`);
    const memberships = await api.get('/club_memberships');
    const users = await api.get('/users');
    
    return committeeMembers
      .map(cm => {
        const membership = memberships.find(m => String(m.id) === String(cm.membership_id));
        const user = membership ? users.find(u => String(u.id) === String(membership.user_id)) : null;
        return {
          ...cm,
          membership,
          user
        };
      })
      .filter(cm => cm.user && cm.user.role === 'student');
  },

  addCommitteeMember: async (committeeId, membershipId, role = 'member') => {
    return await api.post('/committee_memberships', {
      committee_id: committeeId,
      membership_id: membershipId,
      role: role,
      joined_at: istNow()
    });
  },

  updateCommitteeMemberRole: async (committeeMemberId, newRole) => {
    return await api.patch(`/committee_memberships/${committeeMemberId}`, {
      role: newRole
    });
  },

  removeCommitteeMember: async (committeeMemberId) => {
    await api.delete(`/committee_memberships/${committeeMemberId}`);
    return { success: true };
  },



  getCommitteeTasks: async (clubId, committeeId) => {
    // Return empty array for now since volunteer_assignments don't have committee_id mapping easily accessible here
    return [];
  },

  // ── Phase 2: Budgets & Expenses ──
  getClubBudgets: async (clubId) => {
    return await api.get(`/budgets?club_id=${clubId}`);
  },

  getCommitteeBudgets: async (clubId, committeeId) => {
    return await api.get(`/budgets?club_id=${clubId}&committee_id=${committeeId}`);
  },

  allocateCommitteeBudget: async (clubId, committeeId, title, amount, submitterId, parentBudgetId) => {
    const parentBudget = await api.get(`/budgets/${parentBudgetId}`);
    if (!parentBudget) throw new Error("Parent budget not found");
    if (parseFloat(parentBudget.allocated_amount) < parseFloat(amount)) {
      throw new Error("Insufficient funds in main budget");
    }

    // Create the committee budget
    return await api.post('/budgets', {
      club_id: parseInt(clubId, 10),
      committee_id: parseInt(committeeId, 10),
      parent_budget_id: parseInt(parentBudgetId, 10),
      title,
      allocated_amount: amount,
      status: 'approved',
      created_by: parseInt(submitterId, 10),
      created_at: istNow(),
      period_start: istNow(),
      period_end: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString()
    });
  },

  getClubExpenses: async (clubId) => {
    const budgets = await api.get(`/budgets?club_id=${clubId}`);
    const budgetIds = budgets.map(b => String(b.id));
    const allExpenses = await api.get('/expenses');
    const expenses = allExpenses.filter(e => budgetIds.includes(String(e.budget_id)));
    
    // Attach budget name for UI
    return expenses.map(e => ({
      ...e,
      budget: budgets.find(b => String(b.id) === String(e.budget_id))
    }));
  },

  createExpense: async (budgetId, expenseData, submitterId) => {
    return await api.post('/expenses', {
      ...expenseData,
      budget_id: budgetId,
      submitted_by: submitterId,
      status: 'pending',
      treasurer_approved: false,
      president_approved: false,
      created_at: istNow()
    });
  },

  approveExpense: async (expenseId, approverId, approverRole) => {
    const expense = await api.get(`/expenses/${expenseId}`);
    if (!expense) throw new Error('Expense not found');
    
    let updates = {};
    if (approverRole === 'treasurer') {
      updates.treasurer_approved = true;
    } else if (approverRole === 'president') {
      updates.president_approved = true;
    } else {
      throw new Error('Only the Treasurer or President can approve expenses.');
    }

    if ((expense.treasurer_approved || updates.treasurer_approved) && 
        (expense.president_approved || updates.president_approved)) {
      updates.status = 'approved';
      updates.approval_date = istNow();
    }

    return await api.patch(`/expenses/${expenseId}`, updates);
  },

  // ── Phase 2: Certificates ──
  getUserCertificates: async (userId) => {
    return await api.get(`/documents?owner_id=${userId}&doc_type=certificate`);
  },

  // ── Phase 2: Application Management & Role Transfer ──
  withdrawApplication: async (membershipId) => {
    return await api.delete(`/club_memberships/${membershipId}`);
  },

  transferPresidency: async (clubId, currentPresidentMembershipId, newPresidentMembershipId) => {
    // Demote current president to VP
    await api.patch(`/club_memberships/${currentPresidentMembershipId}`, { role_in_club: 'vice_president' });
    // Promote new member to President
    await api.patch(`/club_memberships/${newPresidentMembershipId}`, { role_in_club: 'president' });
    return { success: true };
  },

  getClubAnalytics: async (clubId) => {
    // Fetch raw data from existing tables
    const membersRes = await api.get(`/club_memberships?club_id=${clubId}&status=approved`);
    const eventsRes = await api.get(`/events?club_id=${clubId}`);
    const tasksRes = await api.get('/volunteer_assignments');
    const budgetsRes = await api.get(`/budgets?club_id=${clubId}`);
    const expensesRes = await api.get('/expenses');
    const attendanceRes = await api.get('/attendance_records');
    const registrationsRes = await api.get('/event_registrations');

    const members = membersRes;
    const events = eventsRes;
    const allTasks = tasksRes;
    const budgets = budgetsRes;
    const expenses = expensesRes;
    
    // Filter tasks for this club by finding its events first
    const eventIds = new Set(events.map(e => String(e.id)));
    const tasks = allTasks.filter(t => eventIds.has(String(t.event_id)));

    // Generate 6-month membership growth timeline
    const membershipGrowth = [];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    let cumulative = Math.max(1, members.length - 12);
    months.forEach(month => {
      // Very basic mock growth if dates aren't fully filled out
      // In a real app this would group by members.joined_at
      cumulative += Math.floor(Math.random() * 2);
      membershipGrowth.push({ month, members: cumulative });
    });
    membershipGrowth[membershipGrowth.length - 1].members = members.length;

    // Event attendance vs registrations
    const eventAttendance = events.slice(0, 6).map(e => {
      const eId = String(e.id);
      const registeredCount = registrationsRes.filter(r => String(r.event_id) === eId).length;
      const attendedCount = attendanceRes.filter(a => String(a.event_id) === eId && a.status === 'present').length;
      return {
        name: e.title?.substring(0, 15) || 'Event',
        registered: Math.max(registeredCount, 0),
        attended: Math.max(attendedCount, 0)
      };
    });

    // Budget utilization
    const totalAllocated = budgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount || 0), 0);
    const totalSpent = expenses.filter(e => e.status === 'APPROVED').reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
    
    // Expense breakdown by category
    const expenseByCategory = {};
    expenses.filter(e => e.status === 'APPROVED').forEach(e => {
      const cat = e.category || 'Other';
      expenseByCategory[cat] = (expenseByCategory[cat] || 0) + parseFloat(e.amount || 0);
    });
    const expenseDistribution = Object.entries(expenseByCategory).map(([name, value]) => ({ name, value: Math.round(value) }));
    // Add remaining budget as a pie slice
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

  getClubRecentActivity: async (clubId) => {
    const memberships = await api.get(`/club_memberships?club_id=${clubId}`) || [];
    const events = await api.get(`/events?club_id=${clubId}`) || [];
    const announcements = await api.get(`/announcements?club_id=${clubId}`) || [];
    
    let activities = [];

    memberships.forEach(m => {
      activities.push({
        id: `mem-${m.id}`,
        type: 'membership',
        text: `New member joined the club`,
        date: new Date(m.applied_at || Date.now()),
        icon: 'mdi:account-plus',
        color: 'var(--blue)'
      });
    });

    events.forEach(e => {
      activities.push({
        id: `evt-${e.id}`,
        type: 'event',
        text: `New event "${e.title}" scheduled`,
        date: new Date(e.created_at || e.start_at || Date.now()),
        icon: 'mdi:calendar-plus',
        color: 'var(--gold)'
      });
    });

    announcements.forEach(a => {
      activities.push({
        id: `ann-${a.id}`,
        type: 'announcement',
        text: `Announcement posted: "${a.title}"`,
        date: new Date(a.created_at || Date.now()),
        icon: 'mdi:bullhorn',
        color: 'var(--purple)'
      });
    });

    activities.sort((a, b) => b.date - a.date);

    const now = new Date();
    return activities.slice(0, 5).map(a => {
      // Ensure positive diff
      const diffMs = Math.max(0, now - a.date);
      const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHrs / 24);
      let timeStr = '';
      
      if (diffDays > 1) {
        timeStr = `${diffDays} days ago`;
      } else if (diffDays === 1) {
        timeStr = 'Yesterday';
      } else if (diffHrs >= 1) {
        timeStr = `${diffHrs} hours ago`;
      } else {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        timeStr = diffMins > 0 ? `${diffMins} minutes ago` : 'Just now';
      }

      return {
        ...a,
        time: timeStr
      };
    });
  },

  // ── Resources / Documents ──
  getClubResources: async (clubId) => {
    const documents = await api.get('/documents');
    return documents.data.filter(d => String(d.club_id) === String(clubId) && !d.committee_id);
  },

  getCommitteeResources: async (clubId, committeeId) => {
    const documents = await api.get('/documents');
    return documents.filter(d => String(d.club_id) === String(clubId) && String(d.committee_id) === String(committeeId));
  },

  addClubResource: async (clubId, resourceData, userId) => {
    if (!userId) {
      throw new Error("Authentication required to add resources.");
    }
    const newDoc = {
      ...resourceData,
      club_id: parseInt(clubId),
      owner_id: parseInt(userId),
      created_at: istNow()
    };
    const savedDoc = await api.post('/documents', newDoc);
    await logAudit(userId, 'ADD_RESOURCE', `Added club resource: ${savedDoc.title}`, { club_id: clubId, document_id: savedDoc.id });
    return savedDoc;
  },

  deleteClubResource: async (clubId, resourceId, userId) => {
    if (!userId) {
      throw new Error("Authentication required to delete resources.");
    }
    const doc = await api.get(`/documents/${resourceId}`);
    if (String(doc.club_id) !== String(clubId)) {
      throw new Error("Document does not belong to this club.");
    }
    await api.delete(`/documents/${resourceId}`);
    await logAudit(userId, 'DELETE_RESOURCE', `Deleted club resource: ${doc.title}`, { club_id: clubId, document_id: resourceId });
  },

  // ── Audit Logs ──
  getClubAuditLogs: async (clubId) => {
    const logs = await api.get('/audit_logs');
    const filteredLogs = logs.filter(log => String(log.club_id) === String(clubId));
    
    // Sort descending by timestamp
    filteredLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Populate user info for each log
    const users = await api.get('/users');
    return filteredLogs.map(log => ({
      ...log,
      user: users.find(u => String(u.id) === String(log.user_id))
    }));
  },

  // ── Committees (Request Join) ──
  requestJoinCommittee: async (committeeId, userId) => {
    const committee = await api.get(`/committees/${committeeId}`);
    await logAudit(userId, 'COMMITTEE_JOIN_REQUEST', `Requested to join committee: ${committee.name}`, { club_id: committee.club_id, committee_id: committeeId });
    // In a real backend, this would create a request record or notification
    return { success: true, message: 'Request sent' };
  }
};
