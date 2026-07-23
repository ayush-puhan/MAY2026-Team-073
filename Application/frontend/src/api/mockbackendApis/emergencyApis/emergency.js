import { api } from '../../api';
import { logAudit, istNow } from '../auditHelper';

const getNotificationApi = async () => {
  const mod = await import('../notificationApis/notification');
  return mod.notificationApi;
};

export const emergencyApi = {
  submitEmergencyReport: async (data) => {
    const reportData = {
      ...data,
      status: 'reported',
      created_at: istNow(),
      handled_by: null,
      resolved_at: null
    };
    const response = await api.post('/emergency_reports', reportData);

    // Notify system admins and dean
    const users = await api.get('/users');
    const admins = users.filter(u =>
      u.role === 'system_admin' || u.role === 'dean_student_welfare'
    );

    const notificationApi = await getNotificationApi();

    for (const admin of admins) {
      await notificationApi.createNotification({
        userId: admin.id,
        type: 'EMERGENCY_ALERT',
        title: 'New Emergency Report',
        body: `An emergency report has been submitted. Category: ${data.category}.`,
        channel: 'BOTH',
        relatedEntityType: 'EmergencyReport',
        relatedEntityId: response.id
      });
    }

    await logAudit({
      userId: data.reported_by,
      action: 'CREATE',
      entityType: 'EmergencyReport',
      entityId: response.id,
      details: `Submitted emergency report: ${data.category}`
    });

    return response;
  },

  getEmergencyReports: async (filters = {}) => {
    let reports = await api.get('/emergency_reports');

    if (filters.status) {
      reports = reports.filter(r => r.status.toLowerCase() === filters.status.toLowerCase());
    }
    if (filters.category) {
      reports = reports.filter(r => r.category.toLowerCase() === filters.category.toLowerCase());
    }
    if (filters.reported_by) {
      reports = reports.filter(r => String(r.reported_by) === String(filters.reported_by));
    }

    const users = await api.get('/users');

    return reports.map(r => {
      const reporter = users.find(u => String(u.id) === String(r.reported_by));
      const handler = r.handled_by ? users.find(u => String(u.id) === String(r.handled_by)) : null;
      return {
        ...r,
        reporter_name: reporter ? reporter.full_name : 'Unknown',
        handler_name: handler ? handler.full_name : 'Unassigned'
      };
    }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  updateEmergencyStatus: async (reportId, status, handledBy) => {
    const report = await api.get(`/emergency_reports/${reportId}`);

    const updateData = {
      status,
      handled_by: handledBy || report.handled_by
    };

    if (status.toLowerCase() === 'resolved' && report.status.toLowerCase() !== 'resolved') {
      updateData.resolved_at = istNow();
    }

    const updated = await api.patch(`/emergency_reports/${reportId}`, updateData);

    // Notify the reporter
    const notificationApi = await getNotificationApi();
    await notificationApi.createNotification({
      userId: report.reported_by,
      type: 'EMERGENCY_ALERT',
      title: 'Emergency Report Update',
      body: `Your emergency report status has been updated to: ${status}.`,
      channel: 'IN_APP',
      relatedEntityType: 'EmergencyReport',
      relatedEntityId: updated.id
    });

    await logAudit({
      userId: handledBy,
      action: 'UPDATE',
      entityType: 'EmergencyReport',
      entityId: reportId,
      details: `Updated emergency report #${reportId} status to ${status}`
    });

    return updated;
  },

  getActiveEmergencies: async () => {
    const reports = await emergencyApi.getEmergencyReports();
    return reports.filter(r => r.status.toLowerCase() !== 'resolved');
  }
};
