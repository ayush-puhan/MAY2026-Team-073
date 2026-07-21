import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { dashboardIcons } from '../../../icons/registry';
import { EventCard } from '../EventCard/EventCard';
import styles from './EventsCarousel.module.css';

export const EventsCarousel = ({ title, events = [], viewAllLink, emptyMessage = "No events available." }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);

  const mapEventProps = (ev) => {
    const subtitle = ev.date ? ` • ` : (ev.subtitle || 'TBA');
    const colors = ['var(--blue)', 'var(--purple)', 'var(--green)', 'var(--orange)', 'var(--primary)'];
    const color = colors[parseInt(ev.id || 1, 10) % colors.length] || colors[0];
    
    return {
      title: ev.title || 'Untitled Event',
      subtitle: subtitle,
      color: color,
      bannerKeyword: ev.category ? ev.category.toLowerCase() : '',
      icon: dashboardIcons.eventStar,
      onRegister: () => {
        // dummy register logic
        alert('Registration clicked for ' + ev.title);
      },
      onClick: () => setSelectedEvent(ev)
    };
  };

  // Duplicate events to create infinite loop effect if we have events
  const loopEvents = events.length > 0 ? [...events, ...events, ...events] : [];

  return (
    <div className={styles.carouselContainer}>
      <div className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        {viewAllLink && (
          <Link to={viewAllLink} className={styles.viewAll}>
            View All <Icon icon="mdi:arrow-right" />
          </Link>
        )}
      </div>
      
      <div className={styles.scrollWrapper}>
        {events.length > 0 ? (
          <div className={styles.scrollTrack}>
            {loopEvents.map((ev, idx) => (
              <div key={idx} className={styles.slide}>
                <EventCard {...mapEventProps(ev)} />
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.emptyState}>{emptyMessage}</div>
        )}
      </div>

      {selectedEvent && (
        <div className={styles.modalOverlay} onClick={() => setSelectedEvent(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>{selectedEvent.title}</h2>
              <button onClick={() => setSelectedEvent(null)}><Icon icon="mdi:close" width="24" /></button>
            </div>
            <div className={styles.modalBody}>
              <p><strong>Date:</strong> {selectedEvent.date ? new Date(selectedEvent.date).toLocaleString() : 'TBA'}</p>
              <p><strong>Location:</strong> {selectedEvent.location || 'TBA'}</p>
              <p><strong>Category:</strong> {selectedEvent.category || 'General'}</p>
              <p style={{ marginTop: '1rem' }}>{selectedEvent.description || 'Join us for this exciting event! Full details will be announced shortly.'}</p>
              
              <button className={styles.registerBtn} onClick={() => alert('Registered!')}>
                Register Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
