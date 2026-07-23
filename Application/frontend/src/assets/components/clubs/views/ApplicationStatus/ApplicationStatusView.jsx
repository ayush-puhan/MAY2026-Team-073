import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import styles from './ApplicationStatusView.module.css';
import { uiIcons, authIcons } from '../../../../icons/registry';

const ApplicationStatusView = () => {
  const { club, currentUserId } = useOutletContext();
  const [membership, setMembership] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
  }, [club.id]);

  const fetchStatus = async () => {
    try {
      const allPending = await clubsApi.getPendingMemberships(currentUserId);
      const specific = allPending.find(m => String(m.club_id) === String(club.id));
      setMembership(specific);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>Checking status...</div>;

  if (!membership) {
    return (
      <div className={styles.container}>
        <div className={styles.statusBox}>
          <Icon icon={uiIcons.alertCircleOutline} className={styles.icon} />
          <h2>Application Not Found</h2>
          <p>We couldn't find an active application for this club.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Application Status</h2>
          <p>Track your request to join {club.name}</p>
        </div>
      </header>

      <div className={styles.statusBox}>
        <div className={styles.iconWrapper}>
          <Icon icon={uiIcons.clockOutline} className={styles.pendingIcon} />
        </div>
        <h3>Under Review</h3>
        <p className={styles.subtitle}>Your application was submitted on {new Date(membership.applied_at || Date.now()).toLocaleDateString()}</p>
        
        <div className={styles.timeline}>
          <div className={`${styles.timelineStep} ${styles.completed}`}>
            <div className={styles.stepIcon}><Icon icon={authIcons.check} /></div>
            <div className={styles.stepText}>
              <strong>Application Submitted</strong>
              <span>We received your request</span>
            </div>
          </div>
          
          <div className={`${styles.timelineStep} ${styles.active}`}>
            <div className={styles.stepIcon}><Icon icon={uiIcons.dotsHorizontal} /></div>
            <div className={styles.stepText}>
              <strong>Under Review</strong>
              <span>Club leadership is reviewing your application</span>
            </div>
          </div>
          
          <div className={styles.timelineStep}>
            <div className={styles.stepIcon}></div>
            <div className={styles.stepText}>
              <strong>Decision Made</strong>
              <span>You will be notified of the outcome</span>
            </div>
          </div>
        </div>

        <div className={styles.infoBox}>
          <Icon icon={uiIcons.informationOutline} />
          <p>Applications are typically reviewed within 3-5 business days. You will receive a notification once a decision is made.</p>
        </div>
      </div>
    </div>
  );
};

export default ApplicationStatusView;
