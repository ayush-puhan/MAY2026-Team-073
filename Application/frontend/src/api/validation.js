/**
 * ClubConnect Validation Rules
 * Centralized validation for forms across the app.
 */

export const VALIDATION_RULES = {
  password: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumber: true,
    requireSpecial: true,
  },
  email: {
    // Must be a valid email format ending with .edu or common domains
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  },
};

/**
 * Validate email format
 */
export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  if (!VALIDATION_RULES.email.pattern.test(email)) return 'Please enter a valid email address';
  return null;
};

/**
 * Validate password against all rules
 * Returns an object with { isValid, errors[], strength (0-4) }
 */
export const validatePassword = (password) => {
  const errors = [];
  let strength = 0;

  if (!password) return { isValid: false, errors: ['Password is required'], strength: 0 };

  if (password.length < VALIDATION_RULES.password.minLength) {
    errors.push(`At least ${VALIDATION_RULES.password.minLength} characters`);
  } else {
    strength++;
  }

  if (VALIDATION_RULES.password.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('At least one uppercase letter');
  } else if (password.length >= 1) {
    strength++;
  }

  if (VALIDATION_RULES.password.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('At least one lowercase letter');
  }

  if (VALIDATION_RULES.password.requireNumber && !/[0-9]/.test(password)) {
    errors.push('At least one number');
  } else if (password.length >= 1) {
    strength++;
  }

  if (VALIDATION_RULES.password.requireSpecial && !/[^A-Za-z0-9]/.test(password)) {
    errors.push('At least one special character (!@#$%^&*)');
  } else if (password.length >= 1) {
    strength++;
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength: Math.min(strength, 4),
  };
};

/**
 * Validate full name
 */
export const validateName = (name) => {
  if (!name || !name.trim()) return 'Full name is required';
  if (name.trim().length < 2) return 'Name must be at least 2 characters';
  return null;
};

/**
 * Validate date of birth (must be at least 15 years old)
 */
export const validateDOB = (dobString) => {
  if (!dobString) return null; // Optional field if not provided

  const dob = new Date(dobString);
  const now = new Date();
  
  if (isNaN(dob.getTime())) return 'Invalid date format';

  const minAgeDate = new Date(now.getFullYear() - 15, now.getMonth(), now.getDate());
  
  if (dob > now) {
    return 'Date of birth cannot be in the future';
  }
  
  if (dob > minAgeDate) {
    return 'You must be at least 15 years old';
  }

  return null;
};

/**
 * Get strength label from score
 */
export const getStrengthLabel = (strength) => {
  const labels = ['Too short', 'Weak', 'Fair', 'Good', 'Strong'];
  return labels[strength] || labels[0];
};

/**
 * Get strength color CSS class name
 */
export const getStrengthClass = (strength) => {
  const classes = ['', 'weak', 'fair', 'good', 'strong'];
  return classes[strength] || '';
};
