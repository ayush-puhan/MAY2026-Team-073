import { api } from '../../api';

export const authRealApi = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.token);
    localStorage.setItem('user', JSON.stringify(response.user));
    return response;
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

  updateProfile: async (userId, data) => {
    const payload = { ...data };
    if (payload.profile_photo_url && payload.profile_photo_url.startsWith('data:image')) {
      // Base64 or form-data handling will happen automatically if backend supports it
    }
    return await api.patch('/users/profile', payload);
  },

  getFullProfile: async (userId) => {
    return await api.get('/users/profile');
  },

  getDepartments: async () => await api.get('/departments'),
  getPrograms: async () => await api.get('/programs'),
  getInterests: async () => await api.get('/interests'),

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
    switch (role) {
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
