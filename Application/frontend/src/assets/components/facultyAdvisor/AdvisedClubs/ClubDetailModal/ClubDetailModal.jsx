import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from '@iconify/react';
import { StatusBadge } from '../../../ui/StatusBadge/StatusBadge';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import styles from './ClubDetailModal.module.css';

export const ClubDetailModal = ({ clubId, onClose }) => {
  const [club, setClub] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    facultyAdvisorApi.getClubDetail(clubId).then((data) => {
      setClub(data);
      setLoading(false);
    });
    return () => { document.body.style.overflow = 'auto'; };
  }, [clubId]);

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

          {loading || !club ? (
            <div className={styles.loading}>
              <Icon icon="mdi:loading" className="animate-spin" width="28" />
            </div>
          ) : (
            <>
              <div className={styles.header}>
                <h3 className={styles.title}>{club.name}</h3>
                <StatusBadge status={club.status} />
              </div>
              <p className={styles.description}>{club.description}</p>

              <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Members ({club.members?.length || 0})</h4>
                <div className={styles.memberList}>
                  {(club.members || []).map((m) => (
                    <div key={m.id} className={styles.memberRow}>
                      <span>{m.user_name}</span>
                      <span className={styles.memberRole}>{m.role_in_club}</span>
                    </div>
                  ))}
                  {(!club.members || club.members.length === 0) && (
                    <p className={styles.emptyText}>No approved members yet.</p>
                  )}
                </div>
              </div>

              <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Committees</h4>
                {(club.committees || []).length === 0 ? (
                  <p className={styles.emptyText}>No committees set up yet.</p>
                ) : (
                  club.committees.map((c) => (
                    <div key={c.id} className={styles.memberRow}>
                      <span>{c.name}</span>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
};
