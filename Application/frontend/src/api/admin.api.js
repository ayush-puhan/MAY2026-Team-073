import { adminMockApi } from './mockbackendApis/adminApis/admin.mock';
import { adminRealApi } from './backendApis/adminApis/admin.real';

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

export const adminApi = USE_MOCK ? adminMockApi : adminRealApi;
