import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import { clubsApi } from '../../../../api/backendApis/clubsApis/clubs';
import styles from './AnnouncementComposerModal.module.css';

// clubOptions: optional [{ value, label }] — when provided, the composer asks which club to post to.
export const AnnouncementComposerModal = ({ onClose, onSubmit, clubOptions, user }) => {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [clubId, setClubId] = useState(clubOptions?.[0]?.value ?? null);
  const [targetRole, setTargetRole] = useState('ALL');
  const [targetCommittee, setTargetCommittee] = useState('ALL');
  const [committees, setCommittees] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (clubId) {
      clubsApi.getClubCommittees(clubId).then(setCommittees).catch(console.error);
    } else {
      setCommittees([]);
    }
    setTargetCommittee('ALL');
  }, [clubId]);

  const handleSubmit = async () => {
    if (!title.trim() || !body.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit({ title, body, club_id: clubId, target_role: targetRole, target_committee: targetCommittee });
    } finally {
      setSubmitting(false);
    }
  };

  const userRoleInClub = user?.club_memberships?.find(m => String(m.club_id) === String(clubId))?.role_in_club;

  const roleOptions = [
    { value: 'ALL', label: 'All Roles' },
    { value: 'President', label: 'President' },
    { value: 'Treasurer', label: 'Treasurer' },
    { value: 'Secretary', label: 'Secretary' },
    { value: 'Event Coordinator', label: 'Event Coordinator' },
    { value: 'Member', label: 'Member' }
  ].filter(opt => {
    if (!userRoleInClub) return true;
    if (opt.value === 'ALL') return true;
    return opt.value.toLowerCase() !== userRoleInClub.toLowerCase();
  });

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

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Dropdown
              label="Target Role"
              options={roleOptions}
              value={targetRole}
              onChange={setTargetRole}
            />
            {committees.length > 0 && (
              <Dropdown
                label="Target Committee"
                options={[
                  { value: 'ALL', label: 'All Committees' },
                  ...committees.map(c => ({ value: c.id, label: c.name }))
                ]}
                value={targetCommittee}
                onChange={setTargetCommittee}
              />
            )}
          </div>

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
