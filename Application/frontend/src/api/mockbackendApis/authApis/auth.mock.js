import { api } from '../../api';

export const authMockApi = {
  login: async (email, password) => {
    const users = await api.get(`/users?email=${encodeURIComponent(email)}`);
    if (!users || users.length === 0) throw new Error('Invalid email or password');
    const user = users[0];
    if (user.password !== password) throw new Error('Invalid email or password');
    if (!user.is_active) throw new Error('Your account is currently inactive. Contact administration.');
    
    const token = btoa(JSON.stringify({ id: user.id, email: user.email, role: user.role }));
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    return { user, token };
  },

  register: async (userData) => {
    const existing = await api.get(`/users?email=${encodeURIComponent(userData.email)}`);
    if (existing && existing.length > 0) throw new Error('An account with this email already exists');
    
    const existingRoll = await api.get(`/users?roll_number=${encodeURIComponent(userData.roll_number)}`);
    if (existingRoll && existingRoll.length > 0) throw new Error('An account with this roll number already exists');
    
    const newUser = {
      ...userData,
      role: 'student',
      is_active: true,
      email_verified: false,
    };
    const created = await api.post('/users', newUser);
    localStorage.setItem('is_new_user', 'true');
    return created;
  },

  verifyEmail: async (email, otp) => {
    if (otp !== '123456') throw new Error('Invalid OTP. Please enter 123456 for testing.');
    const users = await api.get(`/users?email=${encodeURIComponent(email)}`);
    if (users && users.length > 0) {
      await api.patch(`/users/${users[0].id}`, { email_verified: true });
    }
    return { success: true, message: 'Email verified successfully' };
  },

  forgotPassword: async (email) => {
    const users = await api.get(`/users?email=${encodeURIComponent(email)}`);
    if (!users || users.length === 0) throw new Error('No account found with this email address');
    return new Promise((resolve) =>
      setTimeout(() => resolve({ message: 'Password reset link has been sent to your email' }), 1000)
    );
  },

  updateProfile: async (userId, data) => {
    const payload = { ...data };
    let savedBase64 = null;
    
    if (payload.profile_photo_url && payload.profile_photo_url.startsWith('data:image')) {
      savedBase64 = payload.profile_photo_url;
      delete payload.profile_photo_url;
    }

    const studentProfileData = payload.student_profile;
    delete payload.student_profile;
    const interestsData = payload.interests;
    delete payload.interests;

    const updatedUser = await api.patch(`/users/${userId}`, payload);
    
    if (studentProfileData) {
      const allProfiles = await api.get('/student_profiles');
      const existingProfiles = allProfiles.filter(p => String(p.user_id) === String(userId));
      if (existingProfiles && existingProfiles.length > 0) {
        await api.patch(`/student_profiles/${existingProfiles[0].id}`, studentProfileData);
        updatedUser.student_profile = { ...existingProfiles[0], ...studentProfileData };
      } else {
        const newProfile = await api.post('/student_profiles', { user_id: String(userId), ...studentProfileData });
        updatedUser.student_profile = newProfile;
      }
    }

    if (interestsData) {
      const allInterests = await api.get('/user_interests');
      const existingInterests = allInterests.filter(i => String(i.user_id) === String(userId));
      for (const ei of existingInterests) {
        await api.del(`/user_interests/${ei.id}`);
      }
      const newInterestsList = [];
      for (const iId of interestsData) {
        const ni = await api.post('/user_interests', { user_id: String(userId), interest_id: parseInt(iId, 10) });
        newInterestsList.push(ni);
      }
      updatedUser.interests = newInterestsList.map(ni => ni.interest_id);
    }

    if (savedBase64) {
      updatedUser.profile_photo_url = savedBase64;
    }
    return updatedUser;
  },

  getFullProfile: async (userId) => {
    const user = await api.get(`/users/${userId}`);
    if (user) {
      const allSp = await api.get('/student_profiles');
      const sp = allSp.filter(p => String(p.user_id) === String(userId));
      if (sp && sp.length > 0) user.student_profile = sp[0];
      
      const allUi = await api.get('/user_interests');
      const ui = allUi.filter(i => String(i.user_id) === String(userId));
      if (ui && ui.length > 0) user.interests = ui.map(u => u.interest_id);
      else user.interests = [];
    }
    return user;
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
