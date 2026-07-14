import React from 'react';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import styles from '../ProfileSettingsModal.module.css';

export const SecurityTab = ({
  fullUser,
  formData,
  handleChange,
  isResetting,
  handleResetPassword,
  showSuccess,
  setIsDeleteModalOpen
}) => {
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className={styles.tabPane}>
      <div className={styles.row}>
        <div className={styles.field}>
          <label>Email Address <span className={styles.required}>*</span>
            {fullUser?.email_verified ? (
              <span className={styles.verifiedBadge}><Icon icon="mdi:check-decagram" /> Verified</span>
            ) : (
              fullUser?.auth_provider === 'LOCAL' && (
                <button type="button" className={styles.verifyEmailBtn} onClick={() => showSuccess("Verification link sent!")}>Verify Email</button>
              )
            )}
          </label>
          <input type="email" value={fullUser?.email || ''} disabled className={`${styles.input} ${styles.disabled}`} title="Contact admin to change email" />
        </div>
        <div className={styles.field}>
          <label>University ID</label>
          <input type="text" name="roll_number" value={formData.roll_number} onChange={handleChange} className={styles.input} placeholder="e.g. UID12345" />
        </div>
      </div>

      <div className={`${styles.row} ${styles.passwordRow}`}>
        <div className={styles.field}>
          <label>Password <span className={styles.required}>*</span></label>
          <input type="password" value="********" disabled className={`${styles.input} ${styles.disabled}`} />
        </div>
        <div className={styles.field}>
          <label>&nbsp;</label>
          <div className={styles.resetWrapper}>
            <button type="button" className={styles.resetPwBtn} onClick={handleResetPassword} disabled={isResetting}>
              {isResetting ? 'Sending link...' : 'Reset Password'}
            </button>
          </div>
        </div>
      </div>

      <div className={styles.dangerZone}>
        <div className={styles.dangerInfo}>
          <h4>Delete Account</h4>
          <p>Permanently remove your account and all associated data. This action cannot be undone.</p>
        </div>
        <button type="button" className={styles.deleteBtn} onClick={() => setIsDeleteModalOpen(true)}>
          Delete Account
        </button>
      </div>
    </motion.div>
  );
};
