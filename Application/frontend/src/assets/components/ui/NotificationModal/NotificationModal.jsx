import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import styles from './NotificationModal.module.css';

export const NotificationModal = ({ isOpen, onClose, hasUnread, notifications = [], onMarkAllRead }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      // Ignore clicks on the bell button itself (it handles its own toggle)
      if (event.target.closest('#notification-bell-btn')) return;
      
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={modalRef}
          className={styles.modal}
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
        >
            <div className={styles.header}>
              <h3>Notifications</h3>
              <button 
                className={styles.markReadBtn} 
                onClick={onMarkAllRead}
                disabled={!hasUnread}
              >
                Mark all as read
              </button>
            </div>
            
            <div className={styles.list}>
              {notifications.map(notif => (
                <div key={notif.id} className={`${styles.item} ${!notif.is_read ? styles.unread : ''}`}>
                  <div className={styles.iconWrapper}>
                    <Icon icon="mdi:bell" />
                  </div>
                  <div className={styles.content}>
                    <h4>{notif.title}</h4>
                    <p>{notif.message}</p>
                  </div>
                  {!notif.is_read && <div className={styles.dot} />}
                </div>
              ))}
              {notifications.length === 0 && (
                <div className={styles.empty}>No new notifications</div>
              )}
            </div>
          </motion.div>
      )}
    </AnimatePresence>
  );
};
