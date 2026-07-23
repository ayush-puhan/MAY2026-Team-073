import React, { useMemo } from 'react';
import styles from './EventInfoModal.module.css';
import { Icon } from '@iconify/react';
import { uiIcons, dashboardIcons, landingIcons } from '../../../icons/registry';

const bannerModules = import.meta.glob('../../../images/events/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : '';
};

export const EventInfoModal = ({ event, onClose, onRegisterClick }) => {
  if (!event) return null;

  const bannerImg = useMemo(() => {
    if (event.banner_url) return event.banner_url;
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
        <button className={styles.closeButton} onClick={onClose}>
          <Icon icon={uiIcons.close} />
        </button>
        <img 
          src={bannerImg} 
          alt={event.title} 
          className={styles.banner} 
        />
        
        <div className={styles.content}>
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
              <Icon icon={uiIcons.mapMarker} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Venue</h4>
                <p>{event.venue}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={landingIcons.accountGroup} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Capacity</h4>
                <p>{event.capacity} seats</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={uiIcons.openInNew} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Access</h4>
                <p>{event.is_public ? 'Public' : 'University Only'}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={uiIcons.clockAlertOutline} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Registration Deadline</h4>
                <p>{event.registration_deadline ? formatDate(event.registration_deadline) : 'No deadline'}</p>
              </div>
            </div>
          </div>

          <div className={styles.description}>
            <h4>About Event</h4>
            <p>{event.description}</p>
          </div>

          {event.event_sessions && event.event_sessions.length > 0 && (
            <div className={styles.description}>
              <h4>Event Sessions</h4>
              <ul style={{ listStyleType: 'none', padding: 0, marginTop: '0.5rem' }}>
                {event.event_sessions.map(s => (
                  <li key={s.id} style={{ margin: '0.5rem 0', padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <strong style={{ display: 'block', marginBottom: '0.25rem' }}>{s.title}</strong>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted-foreground)' }}>
                      <Icon icon={dashboardIcons.calendar} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                      <span style={{ verticalAlign: 'middle' }}>
                        {formatDate(s.start_time)} - {formatDate(s.end_time)}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className={styles.footer}>
            <span className={`${styles.status} ${isCompleted ? styles.completed : ''}`}>
              {event.isRegistered ? '✓ Registered' : (event.status?.toUpperCase() || 'SCHEDULED')}
            </span>
            {event.isRegistered ? (
              <div className={styles.footerActions} style={{ display: 'flex', gap: '0.75rem' }}>
                <button 
                  className={styles.btnRegister} 
                  onClick={() => onRegisterClick({ ...event, checkSchedule: true })}
                >
                  Check Schedule
                </button>
                <button 
                  className={styles.btnRegister} 
                  disabled
                >
                  Registered
                </button>
              </div>
            ) : (
              <button 
                className={styles.btnRegister} 
                disabled={isRegistrationClosed}
                onClick={handleRegisterClick}
              >
                {isRegistrationClosed ? 'Registration Closed' : 'Register Now'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
