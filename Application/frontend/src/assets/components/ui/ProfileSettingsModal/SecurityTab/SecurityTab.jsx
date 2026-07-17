import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { authApi } from '@api/authApis/auth';
import { useToast } from '../../../../../context/ToastContext';
import { useSession } from '../../../../../context/SessionContext';
import { Button } from '../../Button/Button';
import { Input } from '../../Input/Input';
import { useNavigate } from 'react-router-dom';
import { ConfirmModal } from '../../ConfirmModal/ConfirmModal';

import styles from '../ProfileSettingsModal.module.css';

export const SecurityTab = ({
  fullUser,
  formData,
  handleChange,
  isAdminOrFaculty
}) => {
  const { showSuccess, showError } = useToast();
  const { logout } = useSession();
  const navigate = useNavigate();
  const [isResetting, setIsResetting] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const triggerVerify = (msg) => (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log("Triggering toast:", msg);
    showSuccess(msg);
  };

  const handleResetPassword = async () => {
    if (!fullUser?.email) return;
    setIsResetting(true);
    try {
      const res = await authApi.forgotPassword(fullUser.email);
      showSuccess(res.message || 'Password reset link sent to your email!');
    } catch (err) {
      showError('Failed to send reset link.');
    } finally {
      setIsResetting(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await authApi.deleteAccount(fullUser.id);
      logout();
      navigate('/login');
    } catch (err) {
      showError("Failed to delete account");
    }
  };

  return (
    <>
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.securityPane}>
        <div className={styles.secSection}>
          <h4 className={styles.secTitle}>Email Addresses</h4>
          <div className={styles.secGrid}>
            <div className={styles.secField}>
              <label>Registered/Primary Email <span className={styles.required}>*</span></label>
              <div className={styles.secInputWrapper}>
                <Input type="email" value={fullUser?.email || ''} disabled className={styles.secInput} />
                {!isAdminOrFaculty && (
                  fullUser?.email_verified ? (
                    <span className={styles.secBadge}><Icon icon="mdi:check-decagram" /> Verified</span>
                  ) : (
                    fullUser?.auth_provider === 'LOCAL' && (
                      <Button variant="outline" size="sm" type="button" className={styles.secVerifyBtn} onClick={triggerVerify("Verification link sent!")}>Verify</Button>
                    )
                  )
                )}
              </div>
            </div>

            {!isAdminOrFaculty && fullUser?.role === 'student' && (
              <div className={styles.secField}>
                <label>Campus Email</label>
                <div className={styles.secInputWrapper}>
                  <Input 
                    type="email" 
                    name="student_profile.institutional_email"
                    value={formData?.student_profile?.institutional_email || ''} 
                    onChange={handleChange}
                    disabled={formData?.student_profile?.is_verified}
                    className={styles.secInput} 
                    placeholder="e.g. you@campus.edu" 
                  />
                  {formData?.student_profile?.institutional_email && (
                    formData?.student_profile?.is_verified ? (
                      <span className={styles.secBadge}><Icon icon="mdi:check-decagram" /> Verified</span>
                    ) : (
                      <Button variant="outline" size="sm" type="button" className={styles.secVerifyBtn} onClick={triggerVerify("Verification link sent to campus email!")}>Verify</Button>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className={styles.secSection}>
          <h4 className={styles.secTitle}>Identity & Security</h4>
          <div className={styles.secGrid}>
            {!isAdminOrFaculty && (
              <div className={styles.secField}>
                <label>University ID</label>
                <Input type="text" name="roll_number" value={formData.roll_number || ''} onChange={handleChange} className={styles.secInput} placeholder="e.g. UID12345" />
              </div>
            )}

            <div className={styles.secField}>
              <label>Password <span className={styles.required}>*</span></label>
              <div className={styles.secPasswordRow}>
                <Input type="password" value="********" disabled className={styles.secInput} />
                <Button variant="outline" type="button" className={styles.secResetBtn} onClick={(e) => { e.preventDefault(); handleResetPassword(); }} disabled={isResetting}>
                  {isResetting ? 'Sending...' : 'Reset Password'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.secDangerZone}>
          <div className={styles.secDangerInfo}>
            <h5>Delete Account</h5>
            <p>Permanently remove your account and all associated data. This cannot be undone.</p>
          </div>
          <Button variant="destructive" type="button" className={styles.secDeleteBtn} onClick={(e) => { e.preventDefault(); setIsDeleteModalOpen(true); }}>
            Delete Account
          </Button>
        </div>
      </motion.div>

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDeleteAccount}
        title="Delete Account"
        message="Are you absolutely sure you want to delete your account? This action cannot be undone."
        confirmText="Delete Account"
        isDanger={true}
      />
    </>
  );
};
