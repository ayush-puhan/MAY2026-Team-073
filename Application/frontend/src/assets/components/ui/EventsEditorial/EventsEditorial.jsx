import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { EventRegistrationModal } from '../EventRegistrationModal/EventRegistrationModal';
import { useToast } from '../../../../context/ToastContext';
import styles from './EventsEditorial.module.css';
import { rewardsIcons, uiIcons } from '../../../icons/registry';

export const EventsEditorial = ({ events }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [registerEvent, setRegisterEvent] = useState(null);
  const { showSuccess } = useToast();

  if (!events || events.length === 0) return null;

  const featuredEvent = events[0];
  const secondaryEvents = events.slice(1, 4);

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
    showSuccess(`You have been registered for ${registerEvent.title}.`);
    setRegisterEvent(null);
  };

  // Dummy overlapping avatars
  const mockAvatars = [
    'https://i.pravatar.cc/100?img=33',
    'https://i.pravatar.cc/100?img=47',
    'https://i.pravatar.cc/100?img=12'
  ];

  return (
    <div className={styles.editorialSection}>
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>Campus Experiences</h2>
        <p className={styles.sectionSubtitle}>Discover what's happening around you</p>
      </div>

      <div className={styles.editorialGrid}>
        
        {/* Featured Card */}
        {featuredEvent && (
          <div className={styles.featuredCanvas}>
            <div className={styles.featuredBg} style={{ backgroundImage: `url(${getBanner(featuredEvent.title)})` }}></div>
            <div className={styles.featuredOverlay}></div>
            
            <div className={styles.featuredTopBar}>
              <span className={styles.tagTrend}><Icon icon={rewardsIcons.trendingUp} /> Trending</span>
              <button className={styles.bookmarkBtn}><Icon icon={uiIcons.bookmarkOutline} /></button>
            </div>

            <div className={styles.featuredContent}>
              <h3 className={styles.featuredTitle}>{featuredEvent.title}</h3>
              <div className={styles.featuredMetaRow}>
                <span className={styles.featuredTime}>{new Date(featuredEvent.start_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                <span className={styles.featuredVenue}>{featuredEvent.venue}</span>
              </div>
              
              <div className={styles.featuredActionRow}>
                <div className={styles.avatarGroup}>
                  {mockAvatars.map((src, i) => <img key={i} src={src} className={styles.avatar} alt="user" />)}
                  <div className={styles.avatarMore}>+99</div>
                </div>
                <button 
                  className={styles.joinBtn}
                  onClick={(e) => { e.stopPropagation(); setRegisterEvent(featuredEvent); }}
                >
                  Join Event <Icon icon={uiIcons.chevronRight} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Secondary Stack (Upcoming) */}
        <div className={styles.rightCol}>
          <div className={styles.rightColHeader}>
            <h3>Upcoming Events</h3>
            <button className={styles.viewAllBtn}>View All</button>
          </div>
          
          <div className={styles.secondaryStack}>
            {secondaryEvents.map((ev, idx) => {
              const dateObj = new Date(ev.start_at);
              return (
                <div key={ev.id || idx} className={styles.secondaryCard} onClick={() => setSelectedEvent(ev)}>
                  <div className={styles.secImg} style={{ backgroundImage: `url(${getBanner(ev.title)})` }}></div>
                  <div className={styles.secInfo}>
                    <p className={styles.secVenue}>{ev.venue}</p>
                    <h4 className={styles.secTitle}>{ev.title}</h4>
                  </div>
                  <Icon icon={uiIcons.chevronRight} className={styles.secArrow} />
                </div>
              );
            })}
          </div>
        </div>

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
