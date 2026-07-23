import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { Button } from '../../../ui/Button/Button';
import styles from './EventDecisionModal.module.css';
import { uiIcons } from '../../../../icons/registry';

export const EventDecisionModal = ({ event, onClose, onDecide }) => {
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submit = async (approval_status) => {
    setSubmitting(true);
    try {
      await onDecide(event.id, approval_status, comments);
    } finally {
      setSubmitting(false);
    }
  };

  const content = (
    <AnimatePresence>
      <div className={styles.overlay} onClick={onClose}>
        <motion.div
          className={styles.modal}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className={styles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>

          <h3 className={styles.title}>{event.title}</h3>
          <p className={styles.meta}>{event.club_name} &middot; {new Date(event.start_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</p>
          <p className={styles.description}>{event.description}</p>

          <textarea
            className={styles.textarea}
            placeholder="Add review comments (optional)"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            rows={3}
          />

          <div className={styles.actions}>
            <Button variant="outline" disabled={submitting} onClick={() => submit('rejected')}>
              Reject
            </Button>
            <Button variant="primary" isLoading={submitting} onClick={() => submit('approved')}>
              Approve
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
