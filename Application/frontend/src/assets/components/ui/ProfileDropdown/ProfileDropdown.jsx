import React, { useState, useRef, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../../../../context/SessionContext';
import styles from './ProfileDropdown.module.css';

export const ProfileDropdown = ({ user, openProfileModal, minimal = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const { logout } = useSession();

  const toggleDropdown = () => setIsOpen(!isOpen);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const formatRole = (roleStr) => {
    if (!roleStr) return 'Student';
    switch (roleStr) {
      case 'system_admin': return 'System Administrator';
      case 'student_affairs_office': return 'University Administrator';
      case 'dean_student_welfare': return 'Dean of Student Welfare';
      case 'faculty_advisor': return 'Faculty Advisor';
      default: return 'Student';
    }
  };

  return (
    <>
      <div className={`${styles.dropdownContainer} ${minimal ? styles.minimalMode : ''}`} ref={dropdownRef}>
        <button className={`${styles.profileBtn} ${isOpen ? styles.active : ''} ${minimal ? styles.minimalBtn : ''}`} onClick={toggleDropdown}>
          <div className={styles.avatar}>
            {user?.avatar ? (
              <img src={user.avatar} alt="Profile" className={styles.avatarImg} />
            ) : (
              <Icon icon="mdi:account" style={{ fontSize: '1.2rem' }} />
            )}
          </div>
          {!minimal && (
            <>
              <div className={styles.userInfo}>
                <span className={styles.userName}>{user?.full_name || user?.name || 'User'}</span>
                <span className={styles.userRole}>{formatRole(user?.role)}</span>
              </div>
              <Icon icon="mdi:chevron-down" />
            </>
          )}
        </button>

        {isOpen && (
          <div className={styles.dropdownMenu}>
            {/* Mobile/Tablet User Info - only visible when header info is hidden */}
            <div className={styles.dropdownHeader}>
              <span className={styles.dropdownName}>{user?.full_name || user?.name || 'User'}</span>
              <span className={styles.dropdownRole}>{formatRole(user?.role)}</span>
            </div>
            
            <button className={styles.menuItem} onClick={() => { setIsOpen(false); openProfileModal(); }}>
              <Icon icon="mdi:account-outline" className={styles.menuIcon} />
              Profile Settings
            </button>
            <div className={styles.divider}></div>
            <button className={`${styles.menuItem} ${styles.logoutBtn}`} onClick={handleLogout}>
              <Icon icon="mdi:logout" className={styles.menuIcon} />
              Log out
            </button>
          </div>
        )}
      </div>
    </>
  );
};
