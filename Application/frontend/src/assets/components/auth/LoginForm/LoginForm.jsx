import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './LoginForm.module.css';
import { authApi } from '../../../../api/auth.api';
import { validateEmail } from '../../../../api/validation';
import { useToast } from '../../../../context/ToastContext';
import { useSession } from '../../../../context/SessionContext';
import { Icon } from '@iconify/react';
import { motion } from 'framer-motion';

export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  
  useEffect(() => {
    const savedEmail = localStorage.getItem('clubconnect_remembered_email');
    if (savedEmail) {
      setEmail(savedEmail);
      setRemember(true);
    }
  }, []);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { showSuccess, showError } = useToast();
  const { login } = useSession();
  const navigate = useNavigate();

  const validate = () => {
    const e = {};
    const emailErr = validateEmail(email);
    if (emailErr) e.email = emailErr;
    if (!password) e.password = 'Password is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setIsLoading(true);
    try {
      const data = await authApi.login(email, password);
      
      if (remember) {
        localStorage.setItem('clubconnect_remembered_email', email);
      } else {
        localStorage.removeItem('clubconnect_remembered_email');
      }

      if (localStorage.getItem('is_new_user') === 'true' && (data.user.role === 'student' || data.user.role === 'applicant')) {
        showSuccess(`Welcome ${data.user.full_name}, complete your profile to get personalized preferences!`);
      } else {
        showSuccess(`Welcome back, ${data.user.full_name}!`);
      }
      
      const r = data.user.role;
      
      // Update session context with the full user object
      login(data.user);

      // Role-based routing using helper
      navigate(authApi.getDashboardRoute(r));
    } catch (err) {
      showError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Welcome back to campus</h1>
      <p className={styles.subtitle}>Sign in to jump back into your clubs, events and conversations.</p>

      <form onSubmit={handleLogin} className={styles.form} noValidate autoComplete="off">
        <div className={styles.fieldGroup}>
          <input type="email" placeholder="Campus email *" className={`${styles.input} ${errors.email ? styles.inputError : ''}`} value={email} onChange={(e) => { setEmail(e.target.value); errors.email && setErrors({...errors, email: null}); }} autoComplete={remember ? "username" : "off"} />
          {errors.email && <span className={styles.errorText}>{errors.email}</span>}
        </div>
        <div className={styles.fieldGroup}>
          <div className={styles.passwordWrapper}>
            <input type={showPassword ? "text" : "password"} placeholder="Password *" className={`${styles.input} ${errors.password ? styles.inputError : ''}`} value={password} onChange={(e) => { setPassword(e.target.value); errors.password && setErrors({...errors, password: null}); }} autoComplete={remember ? "current-password" : "off"} />
            <button type="button" className={styles.eyeBtn} onClick={() => setShowPassword(!showPassword)} aria-label="Toggle password visibility">
              <Icon icon={showPassword ? "mdi:eye-off-outline" : "mdi:eye-outline"} />
            </button>
          </div>
          {errors.password && <span className={styles.errorText}>{errors.password}</span>}
        </div>

        <div className={styles.optionsRow}>
          <label className={styles.rememberLabel}>
            <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className={styles.checkbox} />
            Remember me
          </label>
          <Link to="/forgot-password" className={styles.forgotLink}>Forgot password?</Link>
        </div>

        <motion.button type="submit" className={styles.submitBtn} disabled={isLoading} whileTap={{ scale: 0.98 }}>
          {isLoading ? <Icon icon="mdi:loading" className={styles.spinner} /> : <Icon icon="mdi:arrow-right" />}
          {isLoading ? 'Signing in...' : 'Sign in'}
        </motion.button>

        <div className={styles.divider}>
          <span>or</span>
        </div>

        <button type="button" className={styles.googleBtn} onClick={() => showSuccess('Google Sign-In will be available soon!')}>
          <Icon icon="logos:google-icon" /> Continue with Google
        </button>
      </form>

      <p className={styles.footer}>New here? <Link to="/register" className={styles.footerLink}>Create your ClubConnect profile</Link></p>
    </div>
  );
};
