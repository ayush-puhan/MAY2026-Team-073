import { api } from '../../api';

export const authMockApi = {
  login: async (email, password) => {
    const users = await api.get(`/users?email=${encodeURIComponent(email)}`);
    if (!users || users.length === 0) throw new Error('Invalid email or password');
    const user = users[0];
    if (user.password_hash !== password) throw new Error('Invalid email or password');
    if (!user.is_active) throw new Error('Your account is currently inactive. Contact administration.');
    
    // Fetch full profile data (student_profile + interests) in parallel
    const parsedId = isNaN(Number(user.id)) ? user.id : Number(user.id);
    const [spArr, uiArr] = await Promise.all([
      api.get(`/student_profiles?user_id=${parsedId}`),
      api.get(`/user_interests?user_id=${parsedId}`)
    ]);
    if (spArr && spArr.length > 0) user.student_profile = spArr[0];
    user.interests = (uiArr && uiArr.length > 0) ? uiArr.map(u => u.interest_id) : [];

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
      password_hash: userData.password,
      is_active: true,
      email_verified: false,
      role: 'student',
      created_at: new Date().toISOString()
    };
    delete newUser.password;

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
    const parsedId = isNaN(Number(userId)) ? userId : Number(userId);
    const payload = { ...data };
    let savedBase64 = null;
    
    if (payload.profile_photo_url && payload.profile_photo_url.startsWith('data:image')) {
      savedBase64 = payload.profile_photo_url;
      delete payload.profile_photo_url;
    }

    if (payload.department_id) payload.department_id = parseInt(payload.department_id, 10);

    const studentProfileData = payload.student_profile;
    delete payload.student_profile;
    const interestsData = payload.interests;
    delete payload.interests;

    const updatedUser = await api.patch(`/users/${parsedId}`, payload);
    
    if (studentProfileData) {
      if (studentProfileData.program_id) studentProfileData.program_id = parseInt(studentProfileData.program_id, 10);
      if (studentProfileData.academic_year) studentProfileData.academic_year = parseInt(studentProfileData.academic_year, 10);
      if (studentProfileData.semester) studentProfileData.semester = parseInt(studentProfileData.semester, 10);

      const existingProfiles = await api.get(`/student_profiles?user_id=${parsedId}`);
      
      if (existingProfiles && existingProfiles.length > 0) {
        // Use existing ID if json-server assigned one, otherwise fallback to the first object and assume it updates
        const profileId = existingProfiles[0].id || existingProfiles[0].user_id; 
        try {
          await api.patch(`/student_profiles/${profileId}`, studentProfileData);
        } catch (e) {
          console.warn("Failed to patch student_profile by ID, attempting full replacement or ignoring if mock.");
        }
        updatedUser.student_profile = { ...existingProfiles[0], ...studentProfileData };
      } else {
        const newProfile = await api.post('/student_profiles', { 
          user_id: parsedId, 
          ...studentProfileData,
          created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
        });
        updatedUser.student_profile = newProfile;
      }
    }

    if (interestsData) {
      const existingInterests = await api.get(`/user_interests?user_id=${parsedId}`);
      for (const ei of existingInterests) {
        if (ei.id) await api.del(`/user_interests/${ei.id}`);
      }
      
      const newInterestsList = [];
      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
      for (const iId of interestsData) {
        const ni = await api.post('/user_interests', { 
          user_id: parsedId, 
          interest_id: Number(iId),
          created_at: timestamp
        });
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
    const parsedId = isNaN(Number(userId)) ? userId : Number(userId);
    const [user, spArr, uiArr] = await Promise.all([
      api.get(`/users/${parsedId}`),
      api.get(`/student_profiles?user_id=${parsedId}`),
      api.get(`/user_interests?user_id=${parsedId}`)
    ]);
    if (user) {
      if (spArr && spArr.length > 0) user.student_profile = spArr[0];
      user.interests = (uiArr && uiArr.length > 0) ? uiArr.map(u => u.interest_id) : [];
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
