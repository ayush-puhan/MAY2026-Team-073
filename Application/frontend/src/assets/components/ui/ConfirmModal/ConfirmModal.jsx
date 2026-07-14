import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ConfirmModal.module.css';
import { Icon } from '@iconify/react';

export const ConfirmModal = ({ 
  isOpen, 
  title, 
  message, 
  onConfirm, 
  onCancel, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  type = 'primary' // 'primary' or 'danger'
}) => {
  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <div className={styles.overlay} onClick={onCancel}>
          <motion.div 
            className={styles.modalContent}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            onClick={e => e.stopPropagation()}
          >
            <div className={styles.header}>
              <div className={`${styles.iconWrapper} ${type === 'danger' ? styles.iconDanger : styles.iconPrimary}`}>
                <Icon icon={type === 'danger' ? "mdi:alert-circle-outline" : "mdi:information-outline"} />
              </div>
              <h3 className={styles.title}>{title}</h3>
            </div>
            
            <div className={styles.body}>
              <p>{message}</p>
            </div>
            
            <div className={styles.actions}>
              <button className={styles.cancelBtn} onClick={onCancel}>
                {cancelText}
              </button>
              <button 
                className={`${styles.confirmBtn} ${type === 'danger' ? styles.btnDanger : styles.btnPrimary}`} 
                onClick={onConfirm}
              >
                {confirmText}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  return createPortal(modalContent, document.body);
};
