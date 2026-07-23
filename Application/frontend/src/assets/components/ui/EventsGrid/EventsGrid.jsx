import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { dashboardIcons, uiIcons } from '../../../icons/registry';
import styles from './EventsGrid.module.css';

const bannerModules = import.meta.glob('../../../../images/events/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

export const EventsGrid = ({ events = [] }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);

  if (!events || events.length === 0) {
    return <div className={styles.empty}>No upcoming events found.</div>;
  }

  const featuredEvent = events[0];
  const secondaryEvents = events.slice(1, 3);

  const getBanner = (title = '') => {
    if (banners.length === 0) return '';
    const sum = title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return banners[sum % banners.length];
  };

  const EventModal = ({ event, onClose }) => {
    if (!event) return null;
    const banner = getBanner(event.title);
    
    return (
      <div className={styles.modalOverlay} onClick={onClose}>
        <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
          <div className={styles.modalBanner} style={{ backgroundImage: url($) }}>
            <button className={styles.closeBtn} onClick={onClose}><Icon icon={uiIcons.close} /></button>
          </div>
          <div className={styles.modalBody}>
            <div className={styles.modalHeaderInfo}>
              <span className={styles.categoryPill}>{event.category || 'General'}</span>
              <h2>{event.title}</h2>
              <div className={styles.modalMeta}>
                <span><Icon icon={uiIcons.calendarClock} /> {event.date ? new Date(event.date).toLocaleString() : 'TBA'}</span>
                <span><Icon icon={uiIcons.mapMarkerOutline} /> {event.location || 'TBA'}</span>
                <span><Icon icon={dashboardIcons.accountGroupOutline} /> 120/150 Seats</span>
              </div>
            </div>
            
            <p className={styles.modalDesc}>{event.description || 'Join us for this exciting event. More details will be shared soon. Don't miss out on this amazing opportunity to connect, learn, and grow with the community.'}</p>
            
            <div className={styles.modalActions}>
              <button className={styles.registerBtn} onClick={() => alert('Processing registration...')}>
                <Icon icon={uiIcons.checkDecagram} width="20" /> Complete Registration
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3><Icon icon={dashboardIcons.events} width="20" /> Upcoming Events</h3>
      </div>
      
      <div className={styles.grid}>
        {featuredEvent && (
          <div className={styles.featuredCard} onClick={() => setSelectedEvent(featuredEvent)}>
            <div className={styles.cardBg} style={{ backgroundImage: url($) }}></div>
            <div className={styles.overlay}></div>
            <div className={styles.featuredContent}>
              <span className={styles.tag}>Featured</span>
              <h2>{featuredEvent.title}</h2>
              <div className={styles.metaRow}>
                <span><Icon icon={uiIcons.clockOutline} /> {featuredEvent.date ? new Date(featuredEvent.date).toLocaleDateString() : 'TBA'}</span>
                <span><Icon icon={uiIcons.mapMarkerOutline} /> {featuredEvent.location || 'TBA'}</span>
              </div>
            </div>
          </div>
        )}

        <div className={styles.secondaryCol}>
          {secondaryEvents.map((ev, idx) => (
            <div key={ev.id || idx} className={styles.compactCard} onClick={() => setSelectedEvent(ev)}>
              <div className={styles.compactImg} style={{ backgroundImage: url($) }}></div>
              <div className={styles.compactInfo}>
                <h4>{ev.title}</h4>
                <span className={styles.compactDate}>{ev.date ? new Date(ev.date).toLocaleDateString() : 'TBA'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <EventModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  );
};
