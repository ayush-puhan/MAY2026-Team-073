import { notificationMockApi } from './mockbackendApis/notificationApis/notification.mock';
import { notificationRealApi } from './backendApis/notificationApis/notification.real';

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

export const notificationApi = USE_MOCK ? notificationMockApi : notificationRealApi;
