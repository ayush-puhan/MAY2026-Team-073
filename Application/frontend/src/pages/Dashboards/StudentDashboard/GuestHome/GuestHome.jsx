import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { useSession } from '../../../../context/SessionContext';
import { useToast } from '../../../../context/ToastContext';
import { EventRegistrationModal } from '../../../../assets/components/ui/EventRegistrationModal/EventRegistrationModal';
import { EventInfoModal } from '../../../../assets/components/ui/EventInfoModal/EventInfoModal';
import { EventCard } from '../../../../assets/components/ui/EventCard/EventCard';
import { eventsApi } from '../../../../api';
import styles from './GuestHome.module.css';
import { uiIcons, calendarIcons, dashboardIcons, rewardsIcons } from '../../../../assets/icons/registry';

export const GuestHome = ({ publicEvents = [], quote, hasOptedOut = false }) => {
  const { user } = useSession();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();
  const [showBanner, setShowBanner] = useState(false);
  const [infoEvent, setInfoEvent] = useState(null);
  const [registerEvent, setRegisterEvent] = useState(null);

  const fullName = user?.full_name || 'Guest';

  useEffect(() => {
    // Respect the "Hide verification reminder" toggle from preferences
    if (hasOptedOut) {
      setShowBanner(false);
      return;
    }
    const dismissed = localStorage.getItem('hideVerifyReminder') === 'true';
    if (!dismissed) setShowBanner(true);
  }, [hasOptedOut]);

  const dismissBanner = () => {
    localStorage.setItem('hideVerifyReminder', 'true');
    setShowBanner(false);
  };

  const handleRegister = async (formData) => {
    try {
      await eventsApi.registerForEvent(registerEvent.id, user?.id, true, formData);
      showSuccess('You have been registered for ' + registerEvent?.title);
      setRegisterEvent(null);
    } catch (err) {
      showError(err.message || 'Failed to register');
    }
  };

  const getTimeOfDay = () => {
    const h = new Date().getHours();
    if (h < 12) return 'morning';
    if (h < 17) return 'afternoon';
    return 'evening';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatTime = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  const upcomingEventsList = publicEvents.filter(ev => ev.status?.toUpperCase() !== 'COMPLETED' && ev.status?.toUpperCase() !== 'CANCELLED');
  const previewEvents = upcomingEventsList.slice(0, 4);
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  return (
    <div className={styles.wrapper}>
      <div className={styles.ambientBg}></div>
      <div className={styles.container}>

        {/* Verification Banner */}
        {showBanner && (
          <div className={styles.banner}>
            <Icon icon={uiIcons.shieldAlertOutline} className={styles.bannerIcon} />
            <div className={styles.bannerText}>
              <strong>Verify Your Account</strong>
              <span>Verify your university email to join clubs, register for events, and unlock the full experience.</span>
            </div>
            <button className={styles.bannerBtn}>Verify Now</button>
            <button className={styles.bannerClose} onClick={dismissBanner}>
              <Icon icon={uiIcons.close} />
            </button>
          </div>
        )}

        {/* Hero */}
        <div className={styles.hero}>
          <span className={styles.heroLabel}>GUEST</span>
          <h1 className={styles.heroTitle}>Good {getTimeOfDay()}, {fullName}.</h1>
          <p className={styles.heroSub}>{quote || 'Explore public events and discover what the university has to offer.'}</p>
          <p className={styles.heroDate}>{today}</p>
        </div>

        {/* Info Cards Row */}
        <div className={styles.infoRow}>
          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon={calendarIcons.calendarToday} className={styles.infoIcon} style={{ color: 'var(--primary)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--primary)' }}>PUBLIC EVENTS</span>
            </div>
            <ul className={styles.infoList}>
              {previewEvents.length > 0 ? previewEvents.map((ev, i) => (
                <li key={ev.id || i} onClick={() => setInfoEvent(ev)}>
                  <span className={styles.dot} style={{ background: 'var(--primary)' }}></span>
                  {ev.title} · {formatTime(ev.start_at)}
                </li>
              )) : (
                <li className={styles.emptyItem}>No public events right now</li>
              )}
            </ul>
          </div>

          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon={dashboardIcons.bullhornOutline} className={styles.infoIcon} style={{ color: 'var(--gold)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--gold)' }}>ANNOUNCEMENTS</span>
            </div>
            <ul className={styles.infoList}>
              <li><span className={styles.dot} style={{ background: 'var(--gold)' }}></span>Welcome to Campus Connect!</li>
              <li><span className={styles.dot} style={{ background: 'var(--gold)' }}></span>Guest access is limited</li>
              <li><span className={styles.dot} style={{ background: 'var(--gold)' }}></span>Verify email to unlock features</li>
            </ul>
          </div>

          <div className={styles.infoCard}>
            <div className={styles.infoHeader}>
              <Icon icon={rewardsIcons.trendingUp} className={styles.infoIcon} style={{ color: 'var(--soft-purple)' }} />
              <span className={styles.infoLabel} style={{ color: 'var(--soft-purple)' }}>WHAT'S HAPPENING</span>
            </div>
            <ul className={styles.infoList}>
              <li><span className={styles.dot} style={{ background: 'var(--soft-purple)' }}></span>{publicEvents.length} public events available</li>
              <li><span className={styles.dot} style={{ background: 'var(--soft-purple)' }}></span>Open registration for guests</li>
              <li><span className={styles.dot} style={{ background: 'var(--soft-purple)' }}></span>Verify to discover clubs</li>
            </ul>
          </div>
        </div>

        {/* Events Preview */}
        <div className={styles.sectionHeader}>
          <h2>Upcoming Events</h2>
          <button className={styles.viewAllBtn} onClick={() => navigate('events')}>
            View All <Icon icon={uiIcons.arrowRight} />
          </button>
        </div>

        <div className={styles.eventsGrid}>
          {previewEvents.map((ev, i) => (
            <EventCard 
              key={ev.id || i}
              icon={dashboardIcons.calendarBlankOutline}
              title={ev.title}
              subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
              university={ev.club?.university?.name || ev.university || "IIT Delhi"}
              rightElement={ev.status}
              bannerKeyword={ev.banner || ev.category?.toLowerCase()}
              onClick={() => setInfoEvent(ev)}
            />
          ))}
        </div>

        {publicEvents.length === 0 && (
          <div className={styles.emptyState}>
            <Icon icon={dashboardIcons.calendarBlankOutline} />
            <p>No public events available right now. Check back soon!</p>
          </div>
        )}

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
        isExternal={true}
      />
    </div>
  );
};
