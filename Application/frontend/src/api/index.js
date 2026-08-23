// Central API Switch File
// This file determines whether to use the mock backend or the real backend
// based on the VITE_USE_MOCK_BACKEND environment variable.

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

// ── Admin APIs ──
import { adminApi as adminMockApi } from './mockbackendApis/adminApis/admin';
import { adminApi as adminRealApi } from './backendApis/adminApis/admin';
export const adminApi = USE_MOCK ? adminMockApi : adminRealApi;

// ── Auth APIs ──
import { authApi as authMockApi } from './mockbackendApis/authApis/auth';
import { authApi as authRealApi } from './backendApis/authApis/auth';
// ALWAYS USE REAL API FOR AUTH NOW
export const authApi = authRealApi;

// ── Student APIs ──
// import { studentApi as studentMockApi } from './mockbackendApis/studentApis/student';
// import { studentApi as studentRealApi } from './backendApis/studentApis/student';
// export const studentApi = USE_MOCK ? studentMockApi : studentMockApi;

// ── Faculty Advisor APIs ──
import { facultyAdvisorApi as facultyAdvisorMockApi } from './mockbackendApis/facultyAdvisorApis/facultyAdvisor';
import { facultyAdvisorApi as facultyAdvisorRealApi } from './backendApis/facultyAdvisorApis/facultyAdvisor';
export const facultyAdvisorApi = USE_MOCK ? facultyAdvisorMockApi : facultyAdvisorRealApi;

// ── University Admin APIs ──
import { universityAdminApi as universityAdminMockApi } from './mockbackendApis/universityAdminApis/universityAdmin';
import { universityAdminApi as universityAdminRealApi } from './backendApis/universityAdminApis/universityAdmin';
export const universityAdminApi = USE_MOCK ? universityAdminMockApi : universityAdminRealApi;

// ── Notification APIs ──
import { notificationApi as notificationMockApi } from './mockbackendApis/notificationApis/notification';
import { notificationApi as notificationRealApi } from './backendApis/notificationApis/notification';
export const notificationApi = USE_MOCK ? notificationMockApi : notificationRealApi;

// ── Announcement APIs ──
import { announcementsApi as announcementsMockApi } from './mockbackendApis/announcementsApis/announcements';
import { announcementsApi as announcementsRealApi } from './backendApis/announcementsApis/announcements';
export const announcementsApi = USE_MOCK ? announcementsMockApi : announcementsRealApi;

// ── Calendar APIs ──
import { calendarMockApi } from './mockbackendApis/calendarApis/calendar';
import { calendarRealApi } from './backendApis/calendarApis/calendar';
export const calendarApi = USE_MOCK ? calendarMockApi : calendarRealApi;

// ── Events APIs ──
import { eventsMockApi } from './mockbackendApis/eventsApis/events';
import { eventsRealApi } from './backendApis/eventsApis/events';
export const eventsApi = USE_MOCK ? eventsMockApi : eventsRealApi;

// ── Clubs APIs ──
import { clubsApi as clubsMockApi } from './mockbackendApis/clubsApis/clubs';
import { clubsApi as clubsRealApi } from './backendApis/clubsApis/clubs';
export const clubsApi = USE_MOCK ? clubsMockApi : clubsRealApi;

// ── Rewards APIs ──
import { rewardsMockApi } from './mockbackendApis/rewardsApis/rewards';
import { rewardsRealApi } from './backendApis/rewardsApis/rewards';
export const rewardsApi = USE_MOCK ? rewardsMockApi : rewardsRealApi;

// ── Emergency APIs ──
import { emergencyApi as emergencyMockApi } from './mockbackendApis/emergencyApis/emergency';
import { emergencyApi as emergencyRealApi } from './backendApis/emergencyApis/emergency';
export const emergencyApi = USE_MOCK ? emergencyMockApi : emergencyRealApi;

import { aiApi } from './backendApis/aiApis/ai';
export { aiApi };

