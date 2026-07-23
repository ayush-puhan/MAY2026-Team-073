import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import styles from './NotificationModal.module.css';
import { uiIcons } from '../../../icons/registry';

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
                    <Icon icon={uiIcons.bell} />
                  </div>
                  <div className={styles.content}>
                    <div className={styles.titleRow}>
                      <h4>{notif.title}</h4>
                      {notif.created_at && (
                        <span className={styles.timestamp}>
                          {new Date(notif.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata',  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                    <p>{notif.body}</p>
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
