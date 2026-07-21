import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { EventCard } from '../../../../assets/components/ui/EventCard/EventCard';
import { EventInfoModal } from '../../../../assets/components/ui/EventInfoModal/EventInfoModal';
import { EventRegistrationModal } from '../../../../assets/components/ui/EventRegistrationModal/EventRegistrationModal';
import { eventsApi } from '../../../../api';
import { useToast } from '../../../../context/ToastContext';
import styles from './VerifiedHome.module.css';

export const VerifiedHome = ({ user, events = [], quote }) => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [infoEvent, setInfoEvent] = useState(null);
  const [registerEvent, setRegisterEvent] = useState(null);
  const fullName = user?.full_name || 'Student';
  
  // Real data mapped from events
  const todayEvents = events.slice(0, 3).map(ev => {
    const d = new Date(ev.start_at);
    const timeStr = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    return { title: ev.title, time: timeStr };
  });

  // Dummy notifications until we hook up a notifications API
  const notifications = [
    { message: 'Rohan invited you to Coding Club', type: 'invite' },
    { message: 'Shaastra: schedule updated', type: 'update' },
    { message: 'Achievement unlocked ✨', type: 'reward' }
  ];

  // Dummy trending until we hook up analytics
  const trending = [
    { title: 'Robotics', subtitle: '+124 this week' },
    { title: 'Design Guild', subtitle: 'Figma jam' },
    { title: 'Aerospace', subtitle: 'rocket launch' }
  ];

  const formatRole = (role) => {
    if (!role) return 'Student';
    return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const handleRegister = async (formData) => {
    try {
      await eventsApi.registerForEvent(registerEvent.id, user.id, false, formData);
      addToast({ title: 'Registration Successful', message: 'You have been registered for ' + registerEvent?.title, type: 'success' });
      setRegisterEvent(null);
      setInfoEvent(null);
    } catch (err) {
      addToast({ title: 'Error', message: 'Failed to register', type: 'error' });
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.ambientBg}></div>
      <div className={styles.container}>
        
        {/* ── Hero Section ── */}
        <div className={styles.hero}>
          <span className={styles.heroLabel}>STUDENT</span>
          <h1 className={styles.heroTitle}>Hi {fullName}, welcome back.</h1>
          <p className={styles.heroSub}>{quote || 'Explore clubs, events & communities'}</p>
          
          <div className={styles.heroPills}>
            <span className={styles.pill}>{user?.email || 'student@clubconnect.edu'}</span>
            <span className={styles.pill}>Role · {formatRole(user?.role)}</span>
          </div>
        </div>

        {/* ── Middle Row ── */}
        <div className={styles.infoRow}>
          {/* Today */}
          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon="mdi:calendar-today" className={styles.infoIcon} style={{ color: 'var(--primary)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--primary)' }}>UPCOMING</span>
            </div>
            <ul className={styles.infoList}>
              {todayEvents.length > 0 ? (
                todayEvents.map((ev, i) => (
                  <li key={i}>
                    <span className={styles.dot} style={{ background: 'var(--primary)' }}></span>
                    {ev.title} · {ev.time}
                  </li>
                ))
              ) : (
                <li style={{ color: 'var(--muted-foreground)', cursor: 'default' }}>No upcoming events today.</li>
              )}
            </ul>
          </div>

          {/* Notifications */}
          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon="mdi:bell-outline" className={styles.infoIcon} style={{ color: 'var(--gold)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--gold)' }}>NOTIFICATIONS</span>
            </div>
            <ul className={styles.infoList}>
              {notifications.map((notif, i) => (
                <li key={i}>
                  <span className={styles.dot} style={{ background: 'var(--gold)' }}></span>
                  {notif.message}
                </li>
              ))}
            </ul>
          </div>

          {/* Trending */}
          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon="mdi:trending-up" className={styles.infoIcon} style={{ color: 'var(--soft-purple)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--soft-purple)' }}>TRENDING</span>
            </div>
            <ul className={styles.infoList}>
              {trending.map((trend, i) => (
                <li key={i}>
                  <span className={styles.dot} style={{ background: 'var(--soft-purple)' }}></span>
                  {trend.title} · {trend.subtitle}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* ── Bottom Row ── */}
        <div className={styles.bottomRow}>
          {/* Progress */}
          <div className={styles.progressCard}>
            <h3 className={styles.cardTitle} style={{ color: 'var(--soft-purple)' }}>YOUR PROGRESS</h3>
            
            <div className={styles.progressBarWrapper}>
              <div className={styles.progressLabel}>
                <span>Profile completion</span>
                <span>72%</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: '72%', background: 'linear-gradient(90deg, var(--primary), var(--gold))' }}></div>
              </div>
            </div>

            <div className={styles.progressBarWrapper}>
              <div className={styles.progressLabel}>
                <span>Certificates earned</span>
                <span>40%</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: '40%', background: 'linear-gradient(90deg, var(--primary), var(--gold))' }}></div>
              </div>
            </div>

            <div className={styles.progressBarWrapper}>
              <div className={styles.progressLabel}>
                <span>Volunteer hours</span>
                <span>55%</span>
              </div>
              <div className={styles.progressTrack}>
                <div className={styles.progressFill} style={{ width: '55%', background: 'linear-gradient(90deg, var(--primary), var(--gold))' }}></div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className={styles.actionsCard}>
            <h3 className={styles.cardTitle} style={{ color: 'var(--gold)' }}>QUICK ACTIONS</h3>
            <div className={styles.actionGrid}>
              <button className={styles.actionBtn} onClick={() => navigate('/student-dashboard/clubs')}>Browse clubs</button>
              <button className={styles.actionBtn} onClick={() => navigate('/student-dashboard/events')}>RSVP an event</button>
              <button className={styles.actionBtn} onClick={() => navigate('/student-dashboard/rewards')}>View certificates</button>
              <button className={styles.actionBtn} onClick={() => navigate('/student-dashboard/announcements')}>Post announcement</button>
            </div>
          </div>
        </div>

        {/* ── Events Grid ── */}
        <div className={styles.sectionHeader} style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Upcoming Events</h2>
          <button className={styles.viewAllBtn} onClick={() => navigate('/student-dashboard/events')} style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
            View All <Icon icon="mdi:arrow-right" />
          </button>
        </div>

        <div className={styles.eventsGrid} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
          {events.slice(0, 3).map((ev, i) => (
            <EventCard 
              key={ev.id || i}
              icon="mdi:calendar-blank-outline"
              title={ev.title}
              subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
              university={ev.club?.university?.name || ev.university || "IIT Delhi"}
              rightElement={ev.status}
              bannerKeyword={ev.banner || ev.category?.toLowerCase()}
              onClick={() => setInfoEvent(ev)}
            />
          ))}
        </div>

      </div>
      
      <EventInfoModal
        event={infoEvent}
        onClose={() => setInfoEvent(null)}
        onRegisterClick={(event) => setRegisterEvent(event)}
      />

      <EventRegistrationModal
        isOpen={!!registerEvent}
        onClose={() => setRegisterEvent(null)}
        event={registerEvent}
        onRegister={handleRegister}
        isExternal={false}
      />
    </div>
  );
};
