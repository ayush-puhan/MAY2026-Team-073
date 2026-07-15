// Valid domains from the university_domains / universities table
const VALID_CAMPUS_DOMAINS = ['iitd.ac.in', 'admin.iitd.ac.in', 'campus.edu', 'bits-pilani.ac.in'];

export const hasCampusDomain = (email) => {
  if (!email) return false;
  const lower = email.toLowerCase();
  
  // Extract domain from email (e.g., "arjun@campus.edu" -> "campus.edu")
  const domain = lower.split('@')[1];
  
  // Check strictly against the database's available university domains
  return VALID_CAMPUS_DOMAINS.includes(domain);
};

export const checkIsVerified = (user) => {
  if (!user) return false;
  
  const role = user.role?.toLowerCase();
  
  // These roles don't need verification checks for features
  if (['faculty_advisor', 'student_affairs_office', 'dean_student_welfare', 'system_admin'].includes(role)) {
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
