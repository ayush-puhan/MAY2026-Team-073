/**
 * Shared audit logging helper for all mock APIs.
 * Logs every action to the audit_logs table in json-server with IST timestamps.
 */
import { api } from '../api';

/** Returns current timestamp in IST (Asia/Kolkata) as a formatted string */
export const istNow = () => {
  return new Date().toLocaleString('en-CA', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  }).replace(',', '');
};

/**
 * Logs an action to the audit_logs table.
 * @param {object} params
 * @param {number|string} params.userId - ID of the user performing the action
 * @param {number} [params.universityId=1] - University scope
 * @param {string} params.action - e.g. 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'APPROVE', 'REJECT'
 * @param {string} params.entityType - e.g. 'User', 'Event', 'Club', 'Expense', 'Announcement'
 * @param {number|string} [params.entityId] - ID of the affected entity
 * @param {string} [params.details] - Human-readable description of what happened
 */
export const logAudit = async ({
  userId,
  universityId = 1,
  action,
  entityType,
  entityId = null,
  details = '',
  ...rest
}) => {
  try {
    const parsedUserId = /^\d+$/.test(String(userId)) ? parseInt(userId, 10) : userId;
    await api.post('/audit_logs', {
      user_id: parsedUserId,
      university_id: universityId,
      action,
      entity_type: entityType,
      entity_id: entityId,
      details,
      created_at: istNow(),
      updated_at: istNow(),
      ...rest
    });
  } catch (err) {
    console.warn('Audit log failed:', err);
  }
};
