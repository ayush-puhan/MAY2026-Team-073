import { universityAdminMockApi } from './mockbackendApis/universityAdminApis/universityAdmin.mock';
import { universityAdminRealApi } from './backendApis/universityAdminApis/universityAdmin.real';

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

export const universityAdminApi = USE_MOCK ? universityAdminMockApi : universityAdminRealApi;
