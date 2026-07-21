import React, { useMemo } from 'react';
import styles from './EventInfoModal.module.css';
import { Icon } from '@iconify/react';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

const bannerModules = import.meta.glob('../../../images/events/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : '';
};

export const EventInfoModal = ({ event, onClose, onRegisterClick }) => {
  if (!event) return null;

  const bannerImg = useMemo(() => {
    const keyword = event.banner || event.category?.toLowerCase() || 'cultural';
    const specificBanner = findBanner(keyword);
    if (specificBanner) return specificBanner;
    
    if (banners.length === 0) return '';
    const titleSum = (event.title || '').split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return banners[titleSum % banners.length];
  }, [event]);

  // Derive if registration is closed
  const isCompleted = event.status?.toUpperCase() === 'COMPLETED';
  const hasDeadlinePassed = event.registration_deadline && new Date(event.registration_deadline) < new Date();
  const isRegistrationClosed = isCompleted || hasDeadlinePassed;

  const handleRegisterClick = () => {
    if (isRegistrationClosed) return;
    onRegisterClick(event);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const d = new Date(dateString);
    return d.toLocaleString('en-US', { 
      month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' 
    });
  };

  const universityName = event.club?.university?.name || "Unknown University";
  const clubName = event.club?.name || "Unknown Club";

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <img 
          src={bannerImg} 
          alt={event.title} 
          className={styles.banner} 
        />
        
        <div className={styles.content}>
          <button className={styles.closeButton} onClick={onClose}>
            <Icon icon={uiIcons.close} />
          </button>

          <div className={styles.header}>
            <h2 className={styles.title}>{event.title}</h2>
            <div className={styles.clubInfo}>
              <span className={styles.clubName}>{clubName}</span>
              <span>•</span>
              <span>{universityName}</span>
            </div>
          </div>

          <div className={styles.detailsGrid}>
            <div className={styles.detailItem}>
              <Icon icon={dashboardIcons.calendar} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Date & Time</h4>
                <p>{formatDate(event.start_at)}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon="mdi:map-marker" className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Venue</h4>
                <p>{event.venue}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon="mdi:account-group" className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Capacity</h4>
                <p>{event.capacity} seats</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon="mdi:open-in-new" className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Access</h4>
                <p>{event.is_public ? 'Public' : 'University Only'}</p>
              </div>
            </div>
          </div>

          <div className={styles.description}>
            <h4>About Event</h4>
            <p>{event.description}</p>
          </div>

          <div className={styles.footer}>
            <span className={`${styles.status} ${isCompleted ? styles.completed : ''}`}>
              {event.status?.toUpperCase() || 'SCHEDULED'}
            </span>
            <button 
              className={styles.btnRegister} 
              disabled={isRegistrationClosed}
              onClick={handleRegisterClick}
            >
              {isRegistrationClosed ? 'Registration Closed' : 'Register Now'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
