import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { Button } from '../../ui/Button/Button';
import { EmptyState } from '../../ui/EmptyState/EmptyState';
import { universityAdminApi } from '../../../../api/universityAdmin.api';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { AnnouncementComposerModal } from '../../dashboard/AnnouncementComposerModal/AnnouncementComposerModal';
import styles from './AnnouncementCenter.module.css';

export const AnnouncementCenter = () => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isComposerOpen, setIsComposerOpen] = useState(false);

  const load = async () => {
    setLoading(true);
    const data = await universityAdminApi.getAnnouncements();
    setAnnouncements(data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handlePublish = async ({ title, body }) => {
    try {
      await universityAdminApi.postAnnouncement({ posted_by: user.id, title, body });
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

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Administrative Communication</h2>
          <p className={styles.subtitle}>Publish university-wide announcements and policy updates.</p>
        </div>
        <Button variant="primary" icon="mdi:plus" onClick={() => setIsComposerOpen(true)}>
          New Announcement
        </Button>
      </div>

      {announcements.length === 0 ? (
        <EmptyState
          icon="mdi:message-outline"
          title="No announcements yet"
          description="Publish a university-wide notice to keep students and clubs informed."
        />
      ) : (
        <div className={styles.list}>
          {announcements.map((a) => (
            <div key={a.id} className={styles.card}>
              <h4 className={styles.cardTitle}>{a.title}</h4>
              <p className={styles.cardBody}>{a.body}</p>
              <span className={styles.cardDate}>{new Date(a.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}

      {isComposerOpen && (
        <AnnouncementComposerModal
          onClose={() => setIsComposerOpen(false)}
          onSubmit={handlePublish}
        />
      )}
    </div>
  );
};
