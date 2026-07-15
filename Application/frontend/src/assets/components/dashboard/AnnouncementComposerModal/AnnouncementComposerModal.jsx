import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import styles from './AnnouncementComposerModal.module.css';

// clubOptions: optional [{ value, label }] — when provided, the composer asks which club to post to.
export const AnnouncementComposerModal = ({ onClose, onSubmit, clubOptions }) => {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [clubId, setClubId] = useState(clubOptions?.[0]?.value ?? null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim() || !body.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit({ title, body, club_id: clubId });
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

          <h3 className={styles.title}>New Announcement</h3>

          {clubOptions && (
            <Dropdown
              label="Club"
              options={clubOptions}
              value={clubId}
              onChange={setClubId}
              placeholder="Select a club"
            />
          )}

          <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Announcement title" />

          <div className={styles.field}>
            <label className={styles.label}>Message</label>
            <textarea
              className={styles.textarea}
              rows={4}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Write your announcement..."
            />
          </div>

          <div className={styles.actions}>
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button variant="primary" isLoading={submitting} onClick={handleSubmit}>Publish</Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
