import { api } from '../../api';

export const aiApi = {
  /**
   * POST /api/ai/chat
   * General AI assistant chat with intent routing, RAG, and Redis caching.
   * @param {string} message - User's chat message
   * @returns {{ status, response, user_context, detected_intent, authorized, sql_context, rag_context, cache_hit }}
   */
  chat: async (message) => {
    const res = await api.post('/ai/chat', { message }, { timeout: 60000 });
    return res;
  },

  /**
   * GET /api/ai/health
   * Health check for Gemini config and knowledge base.
   */
  getHealth: async () => {
    const res = await api.get('/ai/health');
    return res;
  },

  /**
   * POST /api/ai/reports
   * Generate AI-powered reports.
   * @param {string} reportType - One of: student_activity, attendance, membership, reward, support_ticket, volunteer, club_activity, budget, emergency_summary
   */
  generateReport: async (reportType) => {
    const res = await api.post('/ai/reports', { report_type: reportType }, { timeout: 60000 });
    return res;
  },

  /**
   * POST /api/ai/analytics/financial
   * Financial analytics with chart data. Role-restricted.
   */
  financialAnalytics: async () => {
    const res = await api.post('/ai/analytics/financial', {}, { timeout: 60000 });
    return res;
  },

  /**
   * POST /api/ai/analytics/performance
   * Performance analytics scoped to user role.
   */
  performanceAnalytics: async () => {
    const res = await api.post('/ai/analytics/performance', {}, { timeout: 60000 });
    return res;
  },

  /**
   * POST /api/ai/content
   * Generate draft content (announcements, descriptions, etc.)
   * @param {string} contentType - e.g. 'announcement', 'event_description', 'club_description'
   * @param {string} details - Optional free-text context
   */
  generateContent: async (contentType, details = '') => {
    const res = await api.post('/ai/content', { content_type: contentType, details }, { timeout: 60000 });
    return res;
  }
};
