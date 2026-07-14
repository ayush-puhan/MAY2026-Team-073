import { authMockApi } from './mockbackendApis/authApis/auth.mock';
import { authRealApi } from './backendApis/authApis/auth.real';

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

export const authApi = USE_MOCK ? authMockApi : authRealApi;
