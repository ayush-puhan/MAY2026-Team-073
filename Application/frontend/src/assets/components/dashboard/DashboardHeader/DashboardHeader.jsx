import React, { useState } from 'react';
import styles from './DashboardHeader.module.css';
import { ThemeToggle } from '../../ui/ThemeToggle/ThemeToggle';
import { NotificationModal } from '../../ui/NotificationModal/NotificationModal';
import { Icon } from '@iconify/react';
import { useSidebarContext } from '../../../../context/SidebarContext';
import { useSession } from '../../../../context/SessionContext';
import { notificationApi } from '@api/notificationApis/notification';

export const DashboardHeader = () => {
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const { isSidebarOpen, toggleSidebar } = useSidebarContext();
  const { user } = useSession();
  const [notifications, setNotifications] = useState([]);
  const [hasUnread, setHasUnread] = useState(false);

  React.useEffect(() => {
    const fetchNotifs = async () => {
      if (user?.id) {
        try {
          const sorted = await notificationApi.getNotifications(user.id);
          setNotifications(sorted);
          setHasUnread(sorted.some(n => !n.is_read));
        } catch (e) {
          console.error("Failed to fetch notifications", e);
        }
      }
    };
    fetchNotifs();
    // Poll every minute
    const interval = setInterval(fetchNotifs, 60000);
    return () => clearInterval(interval);
  }, [user?.id]);

  const handleMarkAllRead = async () => {
    if (!user?.id) return;
    try {
      await notificationApi.markAllAsRead(user.id);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setHasUnread(false);
    } catch (e) {
      console.error("Failed to mark notifications as read", e);
    }
  };

  return (
    <header className={styles.header}>
      <div className={styles.leftActions}>
        <button className={styles.toggleBtn} onClick={toggleSidebar} data-tooltip={isSidebarOpen ? "Collapse Context Panel" : "Expand Context Panel"}>
          <Icon icon={isSidebarOpen ? "mdi:menu-open" : "mdi:menu"} width="24" height="24" />
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
        notifications={notifications}
        onMarkAllRead={handleMarkAllRead} 
      />
    </header>
  );
};
