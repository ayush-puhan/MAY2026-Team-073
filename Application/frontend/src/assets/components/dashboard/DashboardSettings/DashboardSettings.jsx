import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import styles from './DashboardSettings.module.css';

export const DashboardSettings = () => {
  const { user } = useSession();
  const { showSuccess } = useToast();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [inAppNotifications, setInAppNotifications] = useState(true);

  const handleSave = () => showSuccess('Preferences saved.');

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Settings</h2>
        <p className={styles.subtitle}>Manage your account and notification preferences.</p>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Account</h3>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Full Name</span>
          <span className={styles.rowValue}>{user?.full_name}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Email</span>
          <span className={styles.rowValue}>{user?.email}</span>
        </div>
        <div className={styles.row}>
          <span className={styles.rowLabel}>Role</span>
          <span className={styles.rowValue}>{user?.role?.replace(/_/g, ' ')}</span>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Notification Preferences</h3>
        <label className={styles.toggleRow}>
          <span>Email notifications</span>
          <input type="checkbox" checked={emailNotifications} onChange={(e) => setEmailNotifications(e.target.checked)} />
        </label>
        <label className={styles.toggleRow}>
          <span>In-app notifications</span>
          <input type="checkbox" checked={inAppNotifications} onChange={(e) => setInAppNotifications(e.target.checked)} />
        </label>
        <button className={styles.saveBtn} onClick={handleSave}>
          <Icon icon="mdi:content-save-outline" />
          Save Preferences
        </button>
      </div>
    </div>
  );
};
