import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Icon } from '@iconify/react';
import styles from './Sidebar.module.css';
import { ProfileDropdown } from '../../ui/ProfileDropdown/ProfileDropdown';
import { ProfileSettingsModal } from '../../ui/ProfileSettingsModal/ProfileSettingsModal';
import { useSession } from '../../../../context/SessionContext';
import { useSidebarContext } from '../../../../context/SidebarContext';

export const Sidebar = ({ links = [] }) => {
  const { user } = useSession();
  const { isSidebarOpen } = useSidebarContext();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('is_new_user') === 'true') {
      setIsProfileModalOpen(true);
      localStorage.removeItem('is_new_user');
    }
  }, []);

  return (
    <aside className={`${styles.sidebar} ${!isSidebarOpen ? styles.collapsed : ''}`}>
      <div className={styles.logoArea}>
        <Link to="/" className={styles.logoLink} data-tooltip="Landing Page">
          <img src="/logo.svg" alt="ClubConnect" className={styles.logoImg} />
        </Link>
      </div>

      <nav className={styles.nav}>
        {links.map((link, idx) => (
          <NavLink
            key={idx}
            to={link.path}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive && link.path !== '#' ? styles.active : ''}`
            }
            onClick={(e) => link.path === '#' && e.preventDefault()}
            data-tooltip={link.name}
          >
            <Icon icon={link.icon} className={styles.navIcon} />
            <span className={styles.navLabel}>{link.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className={styles.footer}>
        <ProfileDropdown user={user} openProfileModal={() => setIsProfileModalOpen(true)} minimal={true} />
      </div>

      <ProfileSettingsModal 
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        user={user}
      />
    </aside>
  );
};
