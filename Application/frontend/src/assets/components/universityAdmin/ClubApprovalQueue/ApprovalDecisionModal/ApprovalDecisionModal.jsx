import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { Button } from '../../../ui/Button/Button';
import { Dropdown } from '../../../ui/Dropdown/Dropdown';
import styles from './ApprovalDecisionModal.module.css';

// mode: 'request' (approve/reject a club creation request) | 'activation' (assign advisor to an already-approved club)
export const ApprovalDecisionModal = ({ mode = 'request', title, subtitle, facultyOptions, onClose, onDecide }) => {
  const [comments, setComments] = useState('');
  const [facultyAdvisorId, setFacultyAdvisorId] = useState(facultyOptions?.[0]?.value ?? null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async (status) => {
    if (status === 'approved' && !facultyAdvisorId) return;
    setSubmitting(true);
    try {
      await onDecide(status, { comments, facultyAdvisorId });
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
            <Icon icon="mdi:close" />
          </button>

          <h3 className={styles.title}>{title}</h3>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}

          <Dropdown
            label="Assign Faculty Advisor"
            options={facultyOptions}
            value={facultyAdvisorId}
            onChange={setFacultyAdvisorId}
            placeholder="Select a faculty advisor"
          />
          <p className={styles.hint}>Every approved club must have an assigned faculty advisor before activation.</p>

          {mode === 'request' && (
            <textarea
              className={styles.textarea}
              placeholder="Review comments (optional)"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={3}
            />
          )}

          <div className={styles.actions}>
            {mode === 'request' && (
              <Button variant="outline" disabled={submitting} onClick={() => submit('rejected')}>
                Reject
              </Button>
            )}
            <Button variant="primary" isLoading={submitting} disabled={!facultyAdvisorId} onClick={() => submit('approved')}>
              {mode === 'request' ? 'Approve & Activate' : 'Assign & Activate'}
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
