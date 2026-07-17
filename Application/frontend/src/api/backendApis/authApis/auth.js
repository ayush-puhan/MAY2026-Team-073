import { api } from '../../api';

export const authApi = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.token);
    
    // Fetch full profile (with student_profile + interests) immediately
    // The JWT token is now stored, so the interceptor will attach it
    let fullUser;
    try {
      fullUser = await api.get('/users/profile');
    } catch {
      fullUser = response.user; // Fallback to basic user from login response
    }
    localStorage.setItem('user', JSON.stringify(fullUser));
    return { user: fullUser, token: response.token };
  },

  register: async (userData) => {
    const created = await api.post('/auth/register', userData);
    localStorage.setItem('is_new_user', 'true');
    return created;
  },

  verifyEmail: async (email, otp) => {
    return await api.post('/auth/verify-email', { email, otp });
  },

  forgotPassword: async (email) => {
    return await api.post('/auth/forgot-password', { email });
  },

  /**
   * CONTRACT FOR BACKEND TEAM:
   * Expects a unified JSON payload with nested objects. The backend must handle 
   * SQL JOINs, nested inserts, and constraints internally.
   * 
   * Example Payload:
   * {
   *   "full_name": "John Doe",
   *   "phone": "1234567890",
   *   "department_id": 1,
   *   "student_profile": {
   *     "program_id": 2,
   *     "academic_year": 2,
   *     "semester": 3,
   *     "batch": "2024",
   *     "section": "A"
   *   },
   *   "interests": [1, 3, 5]
   * }
   */
  updateProfile: async (userId, data) => {
    const payload = { ...data };
    // Integer type enforcement for strict DB schemas
    if (payload.department_id) payload.department_id = parseInt(payload.department_id, 10);
    if (payload.student_profile) {
      if (payload.student_profile.program_id) payload.student_profile.program_id = parseInt(payload.student_profile.program_id, 10);
      if (payload.student_profile.academic_year) payload.student_profile.academic_year = parseInt(payload.student_profile.academic_year, 10);
      if (payload.student_profile.semester) payload.student_profile.semester = parseInt(payload.student_profile.semester, 10);
    }
    
    if (payload.profile_photo_url && payload.profile_photo_url.startsWith('data:image')) {
      // Base64 or form-data handling will happen automatically if backend supports it
    }
    return await api.patch('/users/profile', payload);
  },

  /**
   * CONTRACT FOR BACKEND TEAM:
   * Must return the user object merged with their `student_profile` (as a nested object) 
   * and `interests` (as an array of integer IDs).
   */
  getFullProfile: async (userId) => {
    return await api.get('/users/profile');
  },

  getDepartments: async () => await api.get('/departments'),
  getPrograms: async () => await api.get('/programs'),
  getInterests: async () => await api.get('/interests'),
  getValidDomains: async () => await api.get('/universities/domains'),

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  getDashboardRoute: (role) => {
    switch (role?.toLowerCase()) {
      case 'student': return '/student-dashboard';
      case 'faculty_advisor': return '/faculty-advisor-dashboard';
      case 'system_admin': return '/admin-dashboard';
      case 'student_affairs_office':
      case 'dean_student_welfare': return '/university-admin-dashboard';
      default: return '/login';
    }
  },

  deleteAccount: async (userId) => {
    await api.del(`/users/${userId}`);
    return true;
  }
};
