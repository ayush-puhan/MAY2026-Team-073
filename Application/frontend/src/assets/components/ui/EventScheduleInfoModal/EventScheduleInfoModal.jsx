import React from 'react';
import styles from './EventScheduleInfoModal.module.css';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';

export const EventScheduleInfoModal = ({ event, onClose }) => {
  if (!event) return null;

  // We check for event_sessions, otherwise fallback to the event's start_at and end_at as a single session
  const sessions = event.event_sessions?.length > 0 
    ? event.event_sessions 
    : [
        {
          id: 'default',
          title: 'Main Event Session',
          venue: event.venue,
          start_at: event.start_at,
          end_at: event.end_at,
          description: event.description || 'Join us for the main event.'
        }
      ];

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const d = new Date(dateString);
    return d.toLocaleString('en-US', { 
      month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' 
    });
  };

  const getSessionStatus = (startStr, endStr) => {
    const now = new Date();
    const start = new Date(startStr);
    const end = new Date(endStr);
    
    if (now < start) return { label: 'Scheduled', color: 'var(--primary)' };
    if (now >= start && now <= end) return { label: 'Ongoing', color: 'var(--success)' };
    return { label: 'Completed', color: 'var(--text-tertiary)' };
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          <Icon icon={uiIcons.close} />
        </button>
        
        <div className={styles.header}>
          <h2>{event.title} - Schedule</h2>
          <p className={styles.subtitle}>Check the session details below.</p>
        </div>
        
        <div className={styles.content}>
          <div className={styles.timeline}>
            {sessions.map((session, index) => {
              const status = getSessionStatus(session.start_at, session.end_at);
              return (
                <div key={session.id || index} className={styles.sessionCard}>
                  <div className={styles.sessionHeader}>
                    <h4>{session.title}</h4>
                    <span 
                      className={styles.statusBadge} 
                      style={{ backgroundColor: status.color + '20', color: status.color }}
                    >
                      {status.label}
                    </span>
                  </div>
                  
                  <div className={styles.sessionDetails}>
                    <div className={styles.detailRow}>
                      <Icon icon={uiIcons.clockOutline} />
                      <span>{formatDate(session.start_at)} - {formatDate(session.end_at)}</span>
                    </div>
                    <div className={styles.detailRow}>
                      <Icon icon={uiIcons.mapMarkerOutline} />
                      <span>{session.venue || event.venue || 'TBA'}</span>
                    </div>
                  </div>
                  
                  {session.description && (
                    <p className={styles.sessionDescription}>{session.description}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
