import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './RegisterForm.module.css';
import { authApi } from '@api/authApis/auth';
import { validateEmail, validatePassword, validateName, getStrengthLabel } from '../../../../api/validation';
import { useToast } from '../../../../context/ToastContext';
import { Icon } from '@iconify/react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { DocumentModal } from '../../ui/DocumentModal/DocumentModal';

export const RegisterForm = () => {
  const [step, setStep] = useState('register'); // 'register' | 'otp'
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '', confirmPassword: '' });
  const [otp, setOtp] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [activeDoc, setActiveDoc] = useState(null);
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const pwResult = useMemo(() => validatePassword(formData.password), [formData.password]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: null });
  };

  const handleBlur = (field) => {
    setTouched({ ...touched, [field]: true });
    const e = {};
    if (field === 'full_name') { const err = validateName(formData.full_name); if (err) e.full_name = err; }
    if (field === 'email') { const err = validateEmail(formData.email); if (err) e.email = err; }
    if (field === 'password' && formData.password && !pwResult.isValid) e.password = pwResult.errors[0];
    if (field === 'confirmPassword' && formData.confirmPassword !== formData.password) e.confirmPassword = 'Passwords do not match';
    setErrors(prev => ({ ...prev, ...e }));
  };

  const validate = () => {
    const e = {};
    const nameErr = validateName(formData.full_name); if (nameErr) e.full_name = nameErr;
    const emailErr = validateEmail(formData.email); if (emailErr) e.email = emailErr;
    if (!pwResult.isValid) e.password = pwResult.errors[0];
    if (formData.password !== formData.confirmPassword) e.confirmPassword = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    if (!agreed) {
      showError('Please agree to the community guidelines and privacy policy to continue.');
      return;
    }
    
    // Simulate sending OTP without saving user to database yet
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      showSuccess('OTP Sent! Please verify your email.');
      setStep('otp'); // Move to verification step
    }, 800);
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    if (otp.length < 6) {
      showError('Please enter a valid 6-digit OTP');
      return;
    }
    setIsLoading(true);
    try {
      // 1. Verify the dummy OTP (frontend only for now)
      if (otp !== '123456') {
        throw new Error('Invalid OTP. Please enter 123456 for testing.');
      }
      
      // 2. Actually register the user in the database now that OTP is valid
      await authApi.register(formData);
      
      // 3. Mark as verified
      await authApi.verifyEmail(formData.email, otp);
      
      showSuccess('Email verified and profile created! You can now log in.');
      navigate('/login');
    } catch (err) {
      showError(err.message || 'Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'otp') {
    return (
      <div className={styles.container}>
        <h1 className={styles.heading}>Verify your email</h1>
        <p className={styles.subtitle}>We've sent a 6-digit verification code to <strong>{formData.email}</strong>. Enter it below to confirm your account.</p>

        <form onSubmit={handleVerifyOTP} className={styles.form}>
          <div className={styles.fieldGroup}>
            <input 
              name="otp" 
              type="text"
              placeholder="Enter OTP (Test: 123456)" 
              className={styles.input} 
              value={otp} 
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
            />
          </div>
          
          <motion.button type="submit" className={styles.submitBtn} disabled={isLoading} whileTap={{ scale: 0.98 }}>
            {isLoading ? <Icon icon="mdi:loading" className={styles.spinner} /> : <Icon icon="mdi:shield-check" />}
            {isLoading ? 'Verifying...' : 'Verify Email'}
          </motion.button>
        </form>

        <p className={styles.footer}>
          Didn't receive code? <button className={styles.policyLink} onClick={() => showSuccess('New code sent!')}>Resend</button>
        </p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Create your campus profile</h1>
      <p className={styles.subtitle}>30 seconds — then jump into clubs, events and conversations.</p>

      <form onSubmit={handleRegister} className={styles.form} noValidate autoComplete="off">
        {/* Hidden honeypot fields to absorb aggressive browser autofill */}
        <input style={{ display: 'none' }} type="text" name="fakeusernameremembered" />
        <input style={{ display: 'none' }} type="password" name="fakepasswordremembered" />
        
        <div className={styles.row}>
          <div className={styles.fieldGroup}>
            <input name="full_name" placeholder="Full name *" className={clsx(styles.input, errors.full_name && styles.inputError)} value={formData.full_name} onChange={handleChange} onBlur={() => handleBlur('full_name')} autoComplete="off" />
            {errors.full_name && <span className={styles.errorText}>{errors.full_name}</span>}
          </div>

          <div className={styles.fieldGroup}>
            <input name="email" type="email" placeholder="Campus email *" className={clsx(styles.input, errors.email && styles.inputError)} value={formData.email} onChange={handleChange} onBlur={() => handleBlur('email')} autoComplete="new-password" />
            {errors.email && <span className={styles.errorText}>{errors.email}</span>}
          </div>
        </div>

        <div className={styles.row}>
          <div className={styles.fieldGroup}>
            <div className={styles.passwordWrapper}>
              <input name="password" type={showPassword ? "text" : "password"} placeholder="Create password *" className={clsx(styles.input, errors.password && styles.inputError)} value={formData.password} onChange={handleChange} onBlur={() => handleBlur('password')} autoComplete="new-password" />
              <button type="button" className={styles.eyeBtn} onClick={() => setShowPassword(!showPassword)} aria-label="Toggle password visibility">
                <Icon icon={showPassword ? "mdi:eye-off-outline" : "mdi:eye-outline"} />
              </button>
            </div>
            {formData.password && (
              <>
                <div className={styles.strengthMeter}>
                  {[1, 2, 3, 4].map((level) => (
                    <div key={level} className={clsx(styles.bar, pwResult.strength >= level && styles[`str${pwResult.strength}`])} />
                  ))}
                </div>
                <span className={styles.strengthLabel}>Strength Â· {getStrengthLabel(pwResult.strength)}</span>
              </>
            )}
            {errors.password && <span className={styles.errorText}>{errors.password}</span>}
          </div>

          <div className={styles.fieldGroup}>
            <div className={styles.passwordWrapper}>
              <input name="confirmPassword" type={showConfirmPassword ? "text" : "password"} placeholder="Confirm password *" className={clsx(styles.input, errors.confirmPassword && styles.inputError)} value={formData.confirmPassword} onChange={handleChange} onBlur={() => handleBlur('confirmPassword')} autoComplete="new-password" />
              <button type="button" className={styles.eyeBtn} onClick={() => setShowConfirmPassword(!showConfirmPassword)} aria-label="Toggle confirm password visibility">
                <Icon icon={showConfirmPassword ? "mdi:eye-off-outline" : "mdi:eye-outline"} />
              </button>
            </div>
            {errors.confirmPassword && <span className={styles.errorText}>{errors.confirmPassword}</span>}
          </div>
        </div>

        <label className={styles.agreeLabel}>
          <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} className={styles.checkbox} />
          <span>I agree to the community <button type="button" onClick={(e) => { e.preventDefault(); e.stopPropagation(); setActiveDoc('guidelines'); }} className={styles.policyLink}>guidelines</button> and <button type="button" onClick={(e) => { e.preventDefault(); e.stopPropagation(); setActiveDoc('privacy'); }} className={styles.policyLink}>privacy policy</button>.</span>
        </label>

        <motion.button type="submit" className={styles.submitBtn} disabled={isLoading} whileTap={{ scale: 0.98 }}>
          {isLoading ? <Icon icon="mdi:loading" className={styles.spinner} /> : <Icon icon="mdi:star-four-points" />}
          {isLoading ? 'Creating...' : 'Create profile'}
        </motion.button>

        <div className={styles.divider}>
          <span>or</span>
        </div>

        <button type="button" className={styles.googleBtn} onClick={() => showSuccess('Google Sign-Up will be available soon!')}>
          <Icon icon="logos:google-icon" /> Continue with Google
        </button>
      </form>

      <div className={styles.benefits}>
        <div className={styles.benefit}><Icon icon="mdi:check" className={styles.checkIcon} /> Instant access to all your campus clubs</div>
        <div className={styles.benefit}><Icon icon="mdi:check" className={styles.checkIcon} /> RSVP to exclusive campus events every month</div>
        <div className={styles.benefit}><Icon icon="mdi:check" className={styles.checkIcon} /> Free student certificates & badges</div>
      </div>

      <p className={styles.footer}>Already have an account? <Link to="/login" className={styles.footerLink}>Sign in</Link></p>
      
      <DocumentModal isOpen={!!activeDoc} onClose={() => setActiveDoc(null)} documentId={activeDoc} />
    </div>
  );
};
