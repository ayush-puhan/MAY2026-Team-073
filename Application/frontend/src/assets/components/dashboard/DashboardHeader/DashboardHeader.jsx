import React, { useState } from 'react';
import styles from './DashboardHeader.module.css';
import { ThemeToggle } from '../../ui/ThemeToggle/ThemeToggle';
import { NotificationModal } from '../../ui/NotificationModal/NotificationModal';
import { Icon } from '@iconify/react';
import { useSidebarContext } from '../../../../context/SidebarContext';

export const DashboardHeader = () => {
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const { isSidebarOpen, toggleSidebar } = useSidebarContext();
  
  const [hasUnread, setHasUnread] = useState(() => {
    return localStorage.getItem('clubconnect_notifications_read') !== 'true';
  });

  const handleMarkAllRead = () => {
    localStorage.setItem('clubconnect_notifications_read', 'true');
    setHasUnread(false);
  };

  return (
    <header className={styles.header}>
      <div className={styles.leftActions}>
        <button className={styles.toggleBtn} onClick={toggleSidebar} data-tooltip={isSidebarOpen ? "Collapse Context Panel" : "Expand Context Panel"}>
          <Icon icon={isSidebarOpen ? "lucide:panel-left-close" : "lucide:panel-left-open"} width="24" height="24" />
        </button>
      </div>

      <div className={styles.actions}>
        <button id="notification-bell-btn" className={`${styles.bellBtn} ${isNotifOpen ? styles.active : ''}`} onClick={() => setIsNotifOpen(!isNotifOpen)}>
          <Icon icon="mdi:bell-outline" />
          {hasUnread && <div className={styles.bellBadge} />}
        </button>
        <ThemeToggle />
      </div>
      <NotificationModal 
        isOpen={isNotifOpen} 
        onClose={() => setIsNotifOpen(false)} 
        hasUnread={hasUnread}
        onMarkAllRead={handleMarkAllRead} 
      />
    </header>
  );
};
