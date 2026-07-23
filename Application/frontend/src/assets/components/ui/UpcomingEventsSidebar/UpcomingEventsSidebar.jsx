import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { EventRegistrationModal } from '../EventRegistrationModal/EventRegistrationModal';
import { useToast } from '../../../../context/ToastContext';
import styles from './UpcomingEventsSidebar.module.css';
import { uiIcons } from '../../../icons/registry';

export const UpcomingEventsSidebar = ({ events }) => {
  const [registerEvent, setRegisterEvent] = useState(null);
  const { showSuccess } = useToast();

  if (!events || events.length === 0) return null;

  const getBanner = (title) => {
    if(!title) return '/assets/campus_banner.png';
    const t = title.toLowerCase();
    if (t.includes('music') || t.includes('concert')) return '/assets/music_banner.png';
    if (t.includes('chess') || t.includes('hackathon')) return '/assets/coding_banner.png';
    if (t.includes('tech') || t.includes('robot')) return '/assets/tech_banner.png';
    if (t.includes('finance') || t.includes('business')) return '/assets/finance_banner.png';
    if (t.includes('art') || t.includes('cultural')) return '/assets/cultural_banner.png';
    return '/assets/campus_banner.png';
  };

  const handleRegisterConfirm = (formData) => {
    showSuccess(`You are registered as ${formData.full_name}`);
    setRegisterEvent(null);
  };

  return (
    <div className={styles.sidebarWrapper}>
      <div className={styles.header}>
        <h3>Upcoming Events</h3>
        <button className={styles.viewAll}>View All</button>
      </div>

      <div className={styles.eventsList}>
        {events.slice(0, 4).map((ev, idx) => (
          <div key={ev.id || idx} className={styles.eventCard} onClick={() => setRegisterEvent(ev)}>
            <div className={styles.imgWrap} style={{ backgroundImage: `url(${getBanner(ev.title)})` }}></div>
            <div className={styles.info}>
              <p className={styles.venue}>{ev.venue}</p>
              <h4>{ev.title}</h4>
            </div>
            <Icon icon={uiIcons.chevronRight} className={styles.arrow} />
          </div>
        ))}
      </div>

      <EventRegistrationModal 
        isOpen={!!registerEvent} 
        onClose={() => setRegisterEvent(null)} 
        event={registerEvent}
        onRegister={handleRegisterConfirm} 
      />
    </div>
  );
};
