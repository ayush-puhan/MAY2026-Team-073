import React from 'react';
import { format } from 'date-fns';
import { Icon } from '@iconify/react';
import { uiIcons, calendarIcons } from '../../../icons/registry';
import styles from './EventDetailsDrawer.module.css';

const EventDetailsDrawer = ({ event, onClose, user }) => {
  if (!event) return null;

  return (
    <div className={styles.drawerOverlay} onClick={onClose}>
      <div className={styles.drawer} onClick={e => e.stopPropagation()}>
        <div className={styles.drawerHeader}>
          <h2>Session Details</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <Icon icon={uiIcons.close} width="24" />
          </button>
        </div>

        <div className={styles.drawerContent}>
          {event.hasConflict && (
            <div className={styles.conflictWarning}>
              <Icon icon={calendarIcons.conflict} width="24" />
              <span>This session overlaps with another event you are registered for!</span>
            </div>
          )}

          <div className={styles.eventClubInfo}>
            <div className={styles.clubLogo} style={{display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden'}}>
              {event.clubLogo ? (
                <img 
                  src={event.clubLogo} 
                  alt={event.clubName} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }} 
                />
              ) : null}
              <Icon 
                icon={uiIcons.folderOpen} 
                width="24" 
                color="var(--muted-foreground)" 
                style={{ display: event.clubLogo ? 'none' : 'block' }}
              />
            </div>
            <div>
              <div className={styles.clubName}>{event.clubName || 'University Event'}</div>
              <span className={`${styles.statusBadge} ${styles[event.status] || ''}`}>
                {event.status || 'Scheduled'}
              </span>
            </div>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Parent Event</span>
            <span className={styles.detailValue}>{event.eventTitle}</span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Session Title</span>
            <span className={styles.detailValue}>{event.sessionTitle}</span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Date & Time</span>
            <span className={styles.detailValue}>
              {format(event.start, 'MMM d, yyyy - h:mm a')} - {format(event.end, 'h:mm a')}
            </span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Venue</span>
            <span className={styles.detailValue}>{event.venue || 'TBA'}</span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Visibility</span>
            <span className={styles.detailValue} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              {event.isPublic ? (
                <><Icon icon={calendarIcons.eventPublic} width="16" /> Public (Cross-University)</>
              ) : (
                <><Icon icon={calendarIcons.eventPrivate} width="16" /> Private (Club/University Only)</>
              )}
            </span>
          </div>
        </div>

        <div className={styles.drawerFooter}>
          {event.isRegistered ? (
            <button className={styles.primaryBtn} disabled>
              You are Registered
            </button>
          ) : (
            <button className={styles.primaryBtn}>
              Register for Event
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventDetailsDrawer;

