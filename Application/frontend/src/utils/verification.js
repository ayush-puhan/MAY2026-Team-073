import { authApi } from '@api/authApis/auth';

export const hasCampusDomain = async (email) => {
  if (!email) return false;
  const lower = email.toLowerCase();
  if (!lower.includes('@')) return false;

  const domain = lower.split('@')[1];
  
  try {
    const res = await authApi.getValidDomains();
    // Support both direct array and object with data property responses
    const domainsData = Array.isArray(res) ? res : (res.data || []);
    // Map objects to strings if they are returned as objects (like { domain: 'iitd.ac.in' })
    const validDomains = domainsData.map(d => typeof d === 'string' ? d : d.domain);
    
    return validDomains.includes(domain);
  } catch (err) {
    console.error('Failed to fetch valid domains:', err);
    return false;
  }
};

export const checkIsVerified = (user) => {
  if (!user) return false;
  
  const role = user.role?.toLowerCase();
  
  // These roles don't need verification checks for features (Staff/Admins)
  if (role !== 'student') {
    return true;
  }
  
  if (role === 'student' || role === 'applicant' || role === 'member') {
    // Rely strictly on the student_profile table for students
    const profile = user.student_profile;
    return profile?.is_verified === 1 || profile?.is_verified === true;
  } else {
    // Similar verify logic for faculty/admin
    // If they have a separate institutional email field or is_verified flag at the root level
    if (user.is_verified === true) return true;
    if (user.institutional_email && user.email === user.institutional_email && user.email_verified) return true;
  }

  return false;
};
