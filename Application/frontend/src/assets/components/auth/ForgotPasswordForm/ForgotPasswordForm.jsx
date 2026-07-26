import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './ForgotPasswordForm.module.css';
import { authApi } from '@api/authApis/auth';
import { useToast } from '../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { motion } from 'framer-motion';
import { uiIcons, authIcons } from '../../../icons/registry';

export const ForgotPasswordForm = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const { showSuccess, showError } = useToast();

  const handleReset = async (e) => {
    e.preventDefault();
    if (!email) return showError('Please enter your email');
    setIsLoading(true);
    try {
      await authApi.forgotPassword(email);
      showSuccess('Reset link sent!');
      setIsSent(true);
    } catch (err) {
      showError(err.message || 'Failed to send reset link');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSent) {
    return (
      <div className={styles.container}>
        <div className={styles.successIcon}>
          <Icon icon={authIcons.emailCheckOutline} />
        </div>
        <h1 className={styles.heading}>Check your email</h1>
        <p className={styles.subtitle}>We've sent password reset instructions to <strong>{email}</strong></p>
        <button className={styles.submitBtn} onClick={() => setIsSent(false)}>
          Did not receive the email?
        </button>
        <Link to="/login" className={styles.backLink}>
          <Icon icon={uiIcons.arrowLeft} className={styles.backIcon} />
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Forgot your password?</h1>
      <p className={styles.subtitle}>Enter your campus email — we'll send a reset link.</p>
      
      <form onSubmit={handleReset} className={styles.form} noValidate>
        <input
          type="email"
          placeholder="Campus email *"
          className={styles.input}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <div className={styles.optionsRow}>
          <Link to="/login" className={styles.inlineBack}>Back to sign in</Link>
        </div>

          <motion.button type="submit" className={styles.submitBtn} disabled={isLoading} whileTap={{ scale: 0.98 }}>
            {isLoading ? <Icon icon={uiIcons.loading} className={styles.spinner} /> : <Icon icon={uiIcons.starFourPoints} />}
            {isLoading ? 'Sending...' : 'Send reset link'}
          </motion.button>

      </form>
    </div>
  );
};
