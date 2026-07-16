import styles from './ConfirmModal.module.css';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';
import { Button } from '../Button/Button';

export const ConfirmModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = "Confirm Action", 
  message = "Are you sure you want to proceed?", 
  confirmText = "Confirm", 
  cancelText = "Cancel",
  type = "danger" // danger, warning, primary
}) => {
  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <div className={styles.overlay} onClick={onClose}>
          <motion.div 
            className={styles.modal} 
            onClick={e => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
          >
            <div className={styles.header}>
              <div className={`${styles.iconWrapper} ${styles[type]}`}>
                <Icon icon={type === 'danger' ? uiIcons.alertOutline : uiIcons.infoOutline} width="24" height="24" />
              </div>
              <h3 className={styles.title}>{title}</h3>
            </div>
            
            <div className={styles.body}>
              <p className={styles.message}>{message}</p>
            </div>
            
            <div className={styles.footer}>
              <Button variant="outline" className={styles.cancelBtn} onClick={onClose}>
                {cancelText}
              </Button>
              <Button 
                variant={type === 'danger' ? 'destructive' : type === 'primary' ? 'primary' : 'secondary'}
                className={`${styles.confirmBtn} ${styles[type + 'Btn']}`} 
                onClick={() => { onConfirm(); onClose(); }}
              >
                {confirmText}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : null;
};
