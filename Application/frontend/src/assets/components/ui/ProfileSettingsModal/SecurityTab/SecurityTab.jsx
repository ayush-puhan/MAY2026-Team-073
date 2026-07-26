import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { authApi } from '@api/authApis/auth';
import { useToast } from '../../../../../context/ToastContext';
import { useSession } from '../../../../../context/SessionContext';
import { Button } from '../../Button/Button';
import { Input } from '../../Input/Input';
import { useNavigate } from 'react-router-dom';
import { ConfirmModal } from '../../ConfirmModal/ConfirmModal';

import styles from '../ProfileSettingsModal.module.css';
import { uiIcons } from '../../../../icons/registry';

export const SecurityTab = ({
  fullUser,
  formData,
  handleChange,
  isAdminOrFaculty
}) => {
  const { showSuccess, showError } = useToast();
  const { logout, updateSessionUser } = useSession();
  const navigate = useNavigate();
  const [isResetting, setIsResetting] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  
  // Inline set password state
  const [showSetPassword, setShowSetPassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [isSettingPassword, setIsSettingPassword] = useState(false);

  const triggerVerify = (msg) => (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log("Triggering toast:", msg);
    showSuccess(msg);
  };

  const handleResetPassword = async () => {
    if (!fullUser?.email) return;
    
    // If Google user has NO password, let them set it inline instead of email link
    if (fullUser?.auth_provider?.toUpperCase() === 'GOOGLE' && !fullUser?.has_password) {
      setShowSetPassword(true);
      return;
    }

    // Otherwise, normal reset link via email
    setIsResetting(true);
    try {
      const res = await authApi.forgotPassword(fullUser.email);
      showSuccess(res.message || 'Password reset link sent to your email!');
    } catch (err) {
      showError('Failed to send link.');
    } finally {
      setIsResetting(false);
    }
  };

  const handleSetPasswordSubmit = async () => {
    if (newPassword.length < 8) {
      showError("Password must be at least 8 characters long.");
      return;
    }
    setIsSettingPassword(true);
    try {
      const res = await authApi.setPassword(newPassword);
      showSuccess(res.message || "Password set successfully!");
      setShowSetPassword(false);
      setNewPassword('');
      // Update local session context so the UI immediately reflects has_password = true
      if (updateSessionUser) {
        updateSessionUser({ ...fullUser, has_password: true });
      } else {
        // Fallback mutate object directly (dirty but works if updateSessionUser isn't available)
        fullUser.has_password = true; 
      }
    } catch (err) {
      showError(err.response?.data?.message || err.message || "Failed to set password");
    } finally {
      setIsSettingPassword(false);
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
                    <span className={styles.secBadge}><Icon icon={uiIcons.checkDecagram} /> Verified</span>
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
                      <span className={styles.secBadge}><Icon icon={uiIcons.checkDecagram} /> Verified</span>
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

            <div className={styles.secField} style={{ gridColumn: '1 / -1' }}>
              <label>Password <span className={styles.required}>*</span></label>
              
              <AnimatePresence>
                {showSetPassword ? (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }} 
                    animate={{ opacity: 1, height: 'auto' }} 
                    exit={{ opacity: 0, height: 0 }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div className={styles.secPasswordSetContainer} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
                      <Input 
                        type="password" 
                        value={newPassword} 
                        onChange={(e) => setNewPassword(e.target.value)} 
                        wrapperClassName={styles.secInput} 
                        placeholder="Enter new password"
                        autoFocus
                      />
                      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-start' }}>
                        <Button variant="primary" type="button" onClick={handleSetPasswordSubmit} disabled={isSettingPassword || newPassword.length < 8}>
                          {isSettingPassword ? 'Saving...' : 'Save Password'}
                        </Button>
                        <Button variant="ghost" type="button" onClick={() => { setShowSetPassword(false); setNewPassword(''); }}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <div className={styles.secPasswordRow}>
                    <Input type="password" value="********" disabled wrapperClassName={styles.secInput} />
                    <Button variant="outline" type="button" className={styles.secResetBtn} onClick={(e) => { e.preventDefault(); handleResetPassword(); }} disabled={isResetting}>
                      {isResetting ? 'Sending...' : (fullUser?.auth_provider?.toUpperCase() === 'GOOGLE' && !fullUser?.has_password ? 'Set Password' : 'Reset Password')}
                    </Button>
                  </div>
                )}
              </AnimatePresence>

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
