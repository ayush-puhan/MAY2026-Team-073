import { useState } from 'react';
import { adminApi } from '../../../../../api/admin.api';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import { USER_ROLES_OPTIONS } from '../../../../../config/enums';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../../icons/registry';
import { ConfirmModal } from '../../../ui/ConfirmModal/ConfirmModal';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import styles from '../UserManagement.module.css';
import modalStyles from './UserDetailModal.module.css';

export const UserDetailModal = ({ user, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null); // 'deactivate', 'activate'

  if (!user) return null;

  const handleStatusToggle = async () => {
    setLoading(true);
    try {
      await adminApi.updateUserStatus(user.id, !user.is_active);
      onUpdate();
    } catch (error) {
      console.error("Failed to update status", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (e) => {
    const newRole = e.target.value;
    if (newRole === user.role) return;
    
    setLoading(true);
    try {
      await adminApi.assignRole(user.id, newRole);
      onUpdate();
    } catch (error) {
      console.error("Failed to change role", error);
    } finally {
      setLoading(false);
    }
  };

  const openConfirm = (action) => {
    setConfirmAction(action);
    setShowConfirm(true);
  };

  const modalContent = (
    <AnimatePresence>
      {user && (
        <div className={modalStyles.overlay} onClick={onClose}>
          <motion.div 
            className={modalStyles.modal} 
            onClick={e => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
          >
            <div className={modalStyles.header}>
          <h3>User Details</h3>
          <button className={modalStyles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} width="24" />
          </button>
        </div>

        <div className={modalStyles.body}>
          <div className={modalStyles.profileSection}>
            <div className={styles.avatar} style={{ width: '64px', height: '64px', fontSize: '2rem' }}>
              {user.full_name?.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className={modalStyles.name}>{user.full_name}</h2>
              {user.role === 'student' && <p className={modalStyles.email}>{user.email}</p>}
              <span className={`${modalStyles.statusBadge} ${user.is_active ? modalStyles.active : modalStyles.inactive}`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          <div className={modalStyles.detailsGrid}>
            <div className={modalStyles.detailItem}>
              <label>Role</label>
              <Dropdown 
                name="role"
                value={user.role} 
                onChange={handleRoleChange} 
                disabled={loading}
                options={USER_ROLES_OPTIONS}
              />
            </div>
            <div className={modalStyles.detailItem}>
              <label>Joined</label>
              <span>{new Date(user.created_at).toLocaleString()}</span>
            </div>
            {user.student_profile && (
              <>
                <div className={modalStyles.detailItem}>
                  <label>Roll Number</label>
                  <span>{user.roll_number || 'N/A'}</span>
                </div>
                <div className={modalStyles.detailItem}>
                  <label>Academic Year</label>
                  <span>{user.student_profile.academic_year || 'N/A'}</span>
                </div>
              </>
            )}
          </div>

          <div className={modalStyles.actionsSection}>
            <h4>Danger Zone</h4>
            <div className={modalStyles.dangerBox}>
              <div>
                <strong>{user.is_active ? 'Deactivate Account' : 'Activate Account'}</strong>
                <p>
                  {user.is_active 
                    ? "Prevent this user from logging in. They will lose access to the platform." 
                    : "Restore this user's access to the platform."}
                </p>
              </div>
              <button 
                className={user.is_active ? modalStyles.dangerBtn : modalStyles.successBtn}
                onClick={() => openConfirm(user.is_active ? 'deactivate' : 'activate')}
                disabled={loading}
              >
                {user.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          </div>
        </div>
        </motion.div>
        
        <ConfirmModal 
          isOpen={showConfirm}
          onClose={() => setShowConfirm(false)}
          onConfirm={handleStatusToggle}
          title={confirmAction === 'deactivate' ? "Deactivate User" : "Activate User"}
          message={`Are you sure you want to ${confirmAction} ${user.full_name}?`}
          confirmText={confirmAction === 'deactivate' ? "Yes, Deactivate" : "Yes, Activate"}
          type={confirmAction === 'deactivate' ? 'danger' : 'primary'}
        />
      </div>
      )}
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
