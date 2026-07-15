import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { EmptyState } from '../../ui/EmptyState/EmptyState';
import { facultyAdvisorApi } from '../../../../api/facultyAdvisor.api';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { AnnouncementComposerModal } from '../../dashboard/AnnouncementComposerModal/AnnouncementComposerModal';
import styles from './CommunicationCenter.module.css';

export const CommunicationCenter = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [announcements, setAnnouncements] = useState([]);
  const [clubs, setClubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isComposerOpen, setIsComposerOpen] = useState(false);

  const load = async () => {
    setLoading(true);
    const [ann, advisedClubs] = await Promise.all([
      facultyAdvisorApi.getAnnouncements(user.id),
      facultyAdvisorApi.getAdvisedClubs(user.id),
    ]);
    setAnnouncements(ann);
    setClubs(advisedClubs);
    setLoading(false);
  };

  useEffect(() => { load(); }, [user.id]);

  const handlePublish = async ({ title, body, club_id }) => {
    try {
      await facultyAdvisorApi.postAnnouncement({ club_id, posted_by: user.id, title, body });
      showSuccess('Announcement published.');
      setIsComposerOpen(false);
      load();
    } catch (err) {
      showError(err.message || 'Failed to publish announcement.');
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon="mdi:loading" className="animate-spin" width="32" />
      </div>
    );
  }

  const clubOptions = clubs.map((c) => ({ value: c.id, label: c.name }));

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Communication Center</h2>
          <p className={styles.subtitle}>Publish notices and guidance to your advised clubs' leadership.</p>
        </div>
        <Button variant="primary" icon="mdi:plus" onClick={() => setIsComposerOpen(true)} disabled={!clubs.length}>
          New Announcement
        </Button>
      </div>

      {announcements.length === 0 ? (
        <EmptyState
          icon="mdi:message-outline"
          title="No announcements yet"
          description="Publish a notice to keep your advised clubs' leadership informed."
        />
      ) : (
        <div className={styles.list}>
          {announcements.map((a) => (
            <div key={a.id} className={styles.card}>
              <div className={styles.cardHeader}>
                <h4 className={styles.cardTitle}>{a.title}</h4>
                <span className={styles.cardClub}>{a.club_name}</span>
              </div>
              <p className={styles.cardBody}>{a.body}</p>
              <span className={styles.cardDate}>{new Date(a.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}

      {isComposerOpen && (
        <AnnouncementComposerModal
          clubOptions={clubOptions}
          onClose={() => setIsComposerOpen(false)}
          onSubmit={handlePublish}
        />
      )}
    </div>
  );
};
