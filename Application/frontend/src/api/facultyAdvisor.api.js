import { facultyAdvisorMockApi } from './mockbackendApis/facultyAdvisorApis/facultyAdvisor.mock';
import { facultyAdvisorRealApi } from './backendApis/facultyAdvisorApis/facultyAdvisor.real';

const USE_MOCK = import.meta.env.VITE_USE_MOCK_BACKEND === 'true';

export const facultyAdvisorApi = USE_MOCK ? facultyAdvisorMockApi : facultyAdvisorRealApi;
