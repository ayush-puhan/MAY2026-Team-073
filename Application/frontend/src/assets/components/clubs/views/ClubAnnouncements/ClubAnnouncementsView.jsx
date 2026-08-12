import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { announcementsApi } from '../../../../../api/backendApis/announcementsApis/announcements';
import { canPostAnnouncement } from '../../../../../utils/clubPermissions';
import { useSession } from '../../../../../context/SessionContext';
import { useToast } from '../../../../../context/ToastContext';
import { AnnouncementComposerModal } from '../../../announcements/Composer/AnnouncementComposerModal';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import styles from './ClubAnnouncementsView.module.css';

export const ClubAnnouncementsView = () => {
  const { club, userRole } = useOutletContext();
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const { user } = useSession();
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    fetchAnnouncements();
  }, [club.id]);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const data = await announcementsApi.getAnnouncements(club.id);
      setAnnouncements(data);
    } catch (err) {
      setError('Failed to load announcements');
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async ({ title, body, club_id, target_role, target_committee }) => {
    try {
      let audience = 'all_members';

      if (target_committee !== 'ALL') {
        audience = 'committee';
      }
      else if (target_role !== 'ALL') {
        audience = 'leadership';
      }

      const payload = {
        posted_by: user.id,
        posted_by_role: user.role.toLowerCase(),
        title,
        body,
        target_audience: audience,
        club_id: club.id
      };
      
      if (audience === 'targeted') {
        payload.target_role = target_role;
        payload.target_committee = target_committee;
      }

      await announcementsApi.postAnnouncement(payload);
      showSuccess('Announcement published.');
      setIsComposerOpen(false);
      fetchAnnouncements();
    } catch (err) {
      showError(err.message || 'Failed to publish announcement.');
    }
  };

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.container}>
          <header className={styles.header}>
            <div>
              <h2>Club Announcements</h2>
              <p>Updates and news for {club.name} members</p>
            </div>
            {canPostAnnouncement(userRole) && (
              <button 
                className={styles.postBtn}
                onClick={() => setIsComposerOpen(true)}
              >
                <Icon icon={uiIcons.plusCircle} /> Post Announcement
              </button>
            )}
          </header>

          <div className={styles.list}>
            {loading ? (
              <div className={styles.loading}>Loading announcements...</div>
            ) : error ? (
              <div className={styles.error}>{error}</div>
            ) : announcements.length === 0 ? (
              <div className={styles.emptyState}>
                <Icon icon={dashboardIcons.announcements} />
                <h3>No Announcements</h3>
                <p>There are no announcements for this club yet.</p>
              </div>
            ) : (
              announcements.map(ann => (
                <div key={ann.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <div className={styles.authorInfo}>
                      <span className={styles.authorName}>{ann.author_name}</span>
                      {ann.author_role && <span className={styles.authorRole}>{ann.author_role}</span>}
                    </div>
                    <span className={styles.time}>{ann.time}</span>
                  </div>
                  <h3 className={styles.title}>{ann.title}</h3>
                  <div className={styles.content} dangerouslySetInnerHTML={{ __html: ann.content }} />
                  {ann.target_audience === 'targeted' && (
                    <div className={styles.badge}>
                      Targeted to: {ann.target_role !== 'ALL' ? (typeof ann.target_role === 'object' ? 'Role' : ann.target_role) : ''} 
                      {ann.target_committee !== 'ALL' ? ` (Committee ${typeof ann.target_committee === 'object' ? 'Assigned' : ann.target_committee})` : ''}
                      {ann.target_role === 'ALL' && ann.target_committee === 'ALL' ? 'Selected Members' : ''}
                    </div>
                  )}
                  {ann.target_audience !== 'targeted' && ann.target_audience !== 'all_members' && (
                    <div className={styles.badge}>Audience: {ann.target_audience?.replace('_', ' ')}</div>
                  )}
                </div>
              ))
            )}
          </div>

          {isComposerOpen && (
            <AnnouncementComposerModal 
              clubOptions={[{ value: club.id, label: club.name }]}
              user={user}
              onClose={() => setIsComposerOpen(false)}
              onSubmit={handlePublish}
            />
          )}
        </div>
      </div>
    </div>
  );
};
