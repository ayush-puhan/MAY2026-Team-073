import React from 'react';
import styles from './ToastContainer.module.css';
import { Icon } from '@iconify/react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const getIconForType = (type) => {
  switch (type) {
    case 'success':
      return 'mdi:check-circle';
    case 'error':
      return 'mdi:alert-circle';
    case 'loading':
      return 'mdi:loading';
    default:
      return 'mdi:information';
  }
};

export const ToastContainer = ({ toasts, removeToast }) => {
  return (
    <div className={styles.container}>
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 50, scale: 0.3 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
            className={clsx(styles.toast, styles[toast.type])}
          >
            <Icon 
              icon={getIconForType(toast.type)} 
              className={clsx(styles.icon, toast.type === 'loading' && styles.spin)} 
            />
            <span className={styles.message}>{toast.message}</span>
            <button className={styles.closeBtn} onClick={() => removeToast(toast.id)}>
              <Icon icon="mdi:close" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
