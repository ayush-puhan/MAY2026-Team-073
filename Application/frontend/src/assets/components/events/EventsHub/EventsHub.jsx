import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { eventsApi } from '../../../../api';
import { useSession } from '../../../../context/SessionContext';
import { EventCard } from '../../ui/EventCard/EventCard';
import { EventInfoModal } from '../../ui/EventInfoModal/EventInfoModal';
import { EventRegistrationModal } from '../../ui/EventRegistrationModal/EventRegistrationModal';
import { EventScheduleInfoModal } from '../../ui/EventScheduleInfoModal/EventScheduleInfoModal';
import { useToast } from '../../../../context/ToastContext';
import { landingIcons, calendarIcons, uiIcons } from '../../../icons/registry';
import { ContextLayout } from '../../ui/ContextLayout/ContextLayout';
import { ContextPanel, ContextPanelSection, ContextPanelLink } from '../../ui/ContextLayout/ContextPanel';
import { SecondaryHeader } from '../../ui/SecondaryHeader/SecondaryHeader';
import { Dropdown } from '../../ui/Dropdown/Dropdown';
import layoutStyles from '../../ui/ContextLayout/ContextLayout.module.css';
import styles from './EventsHub.module.css';

const statusColors = {
  approved: { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981' },
  in_review: { bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' },
  pending: { bg: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' },
  scheduled: { bg: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' },
  cancelled: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' },
  completed: { bg: 'rgba(107, 114, 128, 0.15)', color: '#6b7280' },
  ongoing: { bg: 'rgba(16, 185, 129, 0.15)', color: '#10b981' },
  draft: { bg: 'rgba(107, 114, 128, 0.15)', color: '#9ca3af' }
};

const getEventStatusBadge = (status) => {
  if (!status) return null;
  const key = status.toLowerCase().replace(/\s+/g, '_');
  const style = statusColors[key] || { bg: 'rgba(107, 114, 128, 0.15)', color: '#9ca3af' };
  const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  return (
    <span style={{
      background: style.bg,
      color: style.color,
      padding: '0.2rem 0.6rem',
      borderRadius: '6px',
      fontSize: '0.7rem',
      fontWeight: 700,
      letterSpacing: '0.04em',
      textTransform: 'uppercase',
      whiteSpace: 'nowrap'
    }}>
      {label}
    </span>
  );
};

// ── Time-based event classification ──
const classifyEvent = (ev) => {
  const now = new Date();
  const status = (ev.status || '').toLowerCase();

  // If status is explicitly completed or cancelled, treat as completed
  if (status === 'completed' || status === 'cancelled') return 'completed';

  const startAt = ev.start_at ? new Date(ev.start_at) : null;
  const endAt = ev.end_at ? new Date(ev.end_at) : null;

  // If we have date info, use it for classification
  if (startAt && endAt) {
    if (now > endAt) return 'completed';
    if (now >= startAt && now <= endAt) return 'ongoing';
    return 'upcoming';
  }

  if (startAt) {
    // No end date — if start is in the past, treat as ongoing; future = upcoming
    if (now >= startAt) return 'ongoing';
    return 'upcoming';
  }

  // If status is ongoing, trust it
  if (status === 'ongoing') return 'ongoing';

  // Fallback: treat as upcoming
  return 'upcoming';
};

const timeFilterOptions = [
  { value: 'upcoming', label: '📅 Upcoming' },
  { value: 'ongoing', label: '🔴 Ongoing' },
  { value: 'completed', label: '✅ Completed' },
  { value: 'all', label: '🗂️ All Events' },
];

const DiscoverHeader = ({ title, subtitle, searchQuery, setSearchQuery, activeTab, onTabChange, rightControls }) => {
  const tabs = [
    { id: 'all', label: 'All', icon: 'mdi:view-grid-outline' },
    { id: 'workshop', label: 'Workshops', icon: 'mdi:hammer-wrench' },
    { id: 'sports', label: 'Sports', icon: 'mdi:basketball' },
    { id: 'arts', label: 'Arts', icon: 'mdi:palette' },
    { id: 'academic', label: 'Academic', icon: 'mdi:school-outline' }
  ];

  return (
    <>
      <SecondaryHeader 
        tabs={tabs} 
        activeTab={activeTab} 
        onTabChange={onTabChange} 
        searchQuery={searchQuery} 
        onSearchChange={setSearchQuery} 
        searchPlaceholder="Search events..." 
        rightControls={rightControls}
      />
      {/* Hero Banner */}
      <div className={styles.heroBanner}>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
    </>
  );
};

const filterEventsByTab = (events, tab) => {
  if (tab === 'all') return events;
  
  return events.filter(ev => {
    // 1. Direct match if category or interests exist (from real DB)
    if (ev.interests?.some(i => i.name.toLowerCase() === tab.toLowerCase())) return true;
    if (ev.category?.toLowerCase() === tab.toLowerCase()) return true;
    
    // 2. Fallback matching for mock dataset (which lacks category/interests)
    const t = tab.toLowerCase();
    const banner = ev.banner?.toLowerCase() || '';
    const title = ev.title?.toLowerCase() || '';
    const desc = ev.description?.toLowerCase() || '';
    
    if (t === 'arts' && (banner === 'music' || banner === 'cultural' || title.includes('music') || title.includes('art'))) return true;
    if (t === 'academic' && (banner === 'tech' || banner === 'coding' || banner === 'robotics' || title.includes('hackathon') || title.includes('seminar') || title.includes('academic'))) return true;
    if (t === 'sports' && (banner === 'sports' || title.includes('chess') || title.includes('sports') || title.includes('championship'))) return true;
    if (t === 'workshop' && (title.includes('workshop') || title.includes('bootcamp') || desc.includes('workshop'))) return true;
    
    return false;
  });
};

// ── Reusable grid renderer ──
const EventGrid = ({ events, onRegister, emptyMessage }) => (
  <div className={styles.grid}>
    {events.length > 0 ? (
      events.map(ev => (
        <EventCard 
          key={ev.id}
          title={ev.title}
          subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
          university={ev.club?.university?.name || ev.university || "IIT Delhi"}
          rightElement={getEventStatusBadge(ev.status)}
          bannerKeyword={ev.banner || ev.category?.toLowerCase()}
          bannerUrl={ev.banner_url}
          onClick={() => onRegister(ev)}
        />
      ))
    ) : (
      <div className={styles.emptyState}>
        <Icon icon="mdi:calendar-search" />
        <p>{emptyMessage || 'No events found.'}</p>
      </div>
    )}
  </div>
);

// ── Section header with count badge ──
const SectionHeader = ({ icon, iconColor, label, count }) => (
  <h2 className={styles.sectionTitle}>
    <Icon icon={icon} style={{ color: iconColor }} /> {label}
    {count > 0 && (
      <span style={{
        background: 'var(--surface)',
        color: 'var(--muted-foreground)',
        padding: '0.1rem 0.5rem',
        borderRadius: '10px',
        fontSize: '0.75rem',
        fontWeight: 600,
        marginLeft: '0.25rem',
      }}>{count}</span>
    )}
  </h2>
);

const MyEventsView = ({ onRegister, searchQuery, setSearchQuery, isVerified, myEvents, timeFilter, setTimeFilter }) => {
  const [activeTab, setActiveTab] = useState('registered');
  
  const searchFiltered = myEvents.filter(ev => {
    const q = searchQuery.toLowerCase();
    return (
      ev.title?.toLowerCase().includes(q) || 
      ev.venue?.toLowerCase().includes(q)
    );
  });

  const tabFiltered = filterEventsByTab(searchFiltered, activeTab);

  // Frontend time filtering is no longer needed since backend handles it
  const timeFiltered = tabFiltered;

  const sectionConfig = {
    upcoming: { icon: 'mdi:calendar-clock', color: '#3b82f6', label: 'Upcoming Events' },
    ongoing: { icon: 'mdi:play-circle-outline', color: '#10b981', label: 'Ongoing Events' },
    completed: { icon: 'mdi:check-circle-outline', color: '#6b7280', label: 'Completed Events' },
    all: { icon: 'mdi:view-grid-outline', color: 'var(--primary)', label: 'All Registered Events' },
  };

  const cfg = sectionConfig[timeFilter] || sectionConfig.all;

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent} style={{ paddingTop: '0' }}>
        <DiscoverHeader 
          title="MY EVENTS" 
          subtitle="Events you have registered for." 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
          rightControls={
            <Dropdown
              name="timeFilter"
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              options={timeFilterOptions}
            />
          }
        />
        
        <div className={styles.filterRow}>
          <SectionHeader icon={cfg.icon} iconColor={cfg.color} label={cfg.label} count={timeFiltered.length} />
        </div>
        
        <EventGrid events={timeFiltered} onRegister={onRegister} emptyMessage="No events found in this category." />
      </div>
    </div>
  );
};

const EventsList = ({ events, title, subtitle, onRegister, searchQuery, setSearchQuery, timeFilter, setTimeFilter }) => {
  const [activeTab, setActiveTab] = useState('all');
  
  const searchFiltered = events.filter(ev => {
    const q = searchQuery.toLowerCase();
    return (
      ev.title?.toLowerCase().includes(q) || 
      ev.venue?.toLowerCase().includes(q) ||
      ev.description?.toLowerCase().includes(q) ||
      ev.category?.toLowerCase().includes(q) ||
      ev.interests?.some(i => i.name.toLowerCase().includes(q))
    );
  });

  const tabFiltered = filterEventsByTab(searchFiltered, activeTab);

  // Frontend time filtering is no longer needed since backend handles it
  const timeFiltered = tabFiltered;

  const sectionConfig = {
    upcoming: { icon: 'mdi:calendar-clock', color: '#3b82f6', label: 'Upcoming Events' },
    ongoing: { icon: 'mdi:play-circle-outline', color: '#10b981', label: 'Ongoing Events' },
    completed: { icon: 'mdi:check-circle-outline', color: '#6b7280', label: 'Completed Events' },
    all: { icon: 'mdi:view-grid-outline', color: 'var(--primary)', label: 'All Events' },
  };

  const cfg = sectionConfig[timeFilter];

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent} style={{ paddingTop: '0' }}>
        <DiscoverHeader 
          title={title} 
          subtitle={subtitle} 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
          rightControls={
            <Dropdown
              name="timeFilter"
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              options={timeFilterOptions}
            />
          }
        />
        
        <div className={styles.filterRow}>
          <SectionHeader icon={cfg.icon} iconColor={cfg.color} label={cfg.label} count={finalEvents.length} />
        </div>

        <EventGrid events={finalEvents} onRegister={onRegister} emptyMessage="No events found in this category." />
      </div>
    </div>
  );
};

const AllEventsView = ({ events, onRegister, searchQuery, setSearchQuery, timeFilter, setTimeFilter }) => {
  const [activeTab, setActiveTab] = useState('all');
  
  const isPublicEvent = (ev) => ev.is_public === true || ev.is_public === 1 || ev.is_public === "1";
  
  const searchFiltered = events.filter(ev => {
    const q = searchQuery.toLowerCase();
    return (
      ev.title?.toLowerCase().includes(q) || 
      ev.venue?.toLowerCase().includes(q) ||
      ev.description?.toLowerCase().includes(q) ||
      ev.interests?.some(i => i.name.toLowerCase().includes(q)) ||
      ev.category?.toLowerCase().includes(q) ||
      ev.banner?.toLowerCase().includes(q)
    );
  });

  const tabFiltered = filterEventsByTab(searchFiltered, activeTab);

  // Frontend time filtering is no longer needed since backend handles it
  const timeFiltered = tabFiltered;

  const campusEvents = timeFiltered.filter(ev => !isPublicEvent(ev));
  const publicEvents = timeFiltered.filter(isPublicEvent);

  const sectionConfig = {
    upcoming: { icon: 'mdi:calendar-clock', color: '#3b82f6', label: 'Upcoming' },
    ongoing: { icon: 'mdi:play-circle-outline', color: '#10b981', label: 'Ongoing' },
    completed: { icon: 'mdi:check-circle-outline', color: '#6b7280', label: 'Completed' },
    all: { icon: 'mdi:view-grid-outline', color: 'var(--primary)', label: 'All' },
  };

  const cfg = sectionConfig[timeFilter];

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent} style={{ paddingTop: '0' }}>
        <DiscoverHeader 
          title="DISCOVER ALL EVENTS" 
          subtitle="Explore everything happening on and off campus." 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
          rightControls={
            <Dropdown
              name="timeFilter"
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              options={timeFilterOptions}
            />
          }
        />

        <div className={styles.filterRow}>
          <SectionHeader icon={cfg.icon} iconColor={cfg.color} label={`${cfg.label} Events`} count={timeFiltered.length} />
        </div>
        
        <div className={styles.splitLayout}>
          <div className={styles.categorySection}>
            <h2 className={styles.sectionTitle}>
              <Icon icon="mdi:school-outline" style={{ color: 'var(--primary)' }} /> Campus Exclusive
            </h2>
            <EventGrid events={campusEvents} onRegister={onRegister} emptyMessage="No campus events found." />
          </div>
          
          <div className={styles.categorySection}>
            <h2 className={styles.sectionTitle}>
              <Icon icon="mdi:earth" style={{ color: 'var(--gold)' }} /> Public Events
            </h2>
            <EventGrid events={publicEvents} onRegister={onRegister} emptyMessage="No public events found." />
          </div>
        </div>
      </div>
    </div>
  );
};

export const EventsHub = () => {
  const { user } = useSession();
  const { addToast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [myEvents, setMyEvents] = useState([]);
  const [infoEvent, setInfoEvent] = useState(null);
  const [registerEvent, setRegisterEvent] = useState(null);
  const [scheduleEvent, setScheduleEvent] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [timeFilter, setTimeFilter] = useState('upcoming');

  const isVerified = user?.student_profile?.is_verified === 1 || user?.student_profile?.is_verified === true;
  const isPublicEvent = (ev) => ev.is_public === true || ev.is_public === 1 || ev.is_public === "1";

  useEffect(() => {
    // Auto-close modals on any navigation (e.g. clicking sidebar links)
    setInfoEvent(null);
    setRegisterEvent(null);
    setScheduleEvent(null);
  }, [location.key]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const fetchStatus = timeFilter === 'all' ? '' : timeFilter;
        const data = await eventsApi.getAllEvents({ status: fetchStatus });
        if (!isVerified) {
          const publicOnly = data.filter(isPublicEvent);
          setEvents(publicOnly);
        } else {
          setEvents(data);
        }
      } catch (err) {
        console.error("Failed to load events", err);
      }
    };
    fetchEvents();
  }, [isVerified, timeFilter]);

  useEffect(() => {
    if (user?.id) {
      const isExternal = !isVerified;
      eventsApi.getUserEvents(user.id, isExternal).then(setMyEvents).catch(console.error);
    }
  }, [user?.id, isVerified]);

  const handleInfoEventOpen = (ev) => {
    setInfoEvent({ ...ev, isRegistered: myEvents.some(m => String(m.id) === String(ev.id)) });
  };

  const handleRegister = async (formData) => {
    try {
      await eventsApi.registerForEvent(registerEvent.id, user.id, !isVerified, formData);
      addToast({ title: 'Success', message: `Registered for ${registerEvent?.title}`, type: 'success' });
      
      // Update local state immediately
      setMyEvents(prev => [...prev, registerEvent]);
      window.dispatchEvent(new Event('refreshNotifications'));
      
      setRegisterEvent(null);
      
      // Update the currently viewed event so the modal updates in real-time
      if (infoEvent && infoEvent.id === registerEvent.id) {
        setInfoEvent(prev => ({ ...prev, isRegistered: true }));
      }
    } catch (error) {
      addToast({ title: 'Error', message: 'Failed to register. Please try again.', type: 'error' });
    }
  };

  const publicEvents = events.filter(isPublicEvent);
  const campusEvents = events.filter(ev => !isPublicEvent(ev));

  const basePath = location.pathname.includes('/student-dashboard') ? '/student-dashboard/events' : '/events';

  return (
    <ContextLayout>
      <ContextPanel title="Events Hub">
        <ContextPanelSection title="DISCOVER">
          {isVerified && (
            <ContextPanelLink 
              to={basePath} 
              exact={true} 
              icon={landingIcons.compass} 
              label="All Events" 
            />
          )}
          <ContextPanelLink 
            to={`${basePath}/public`} 
            icon={calendarIcons.eventPublic} 
            label="Public Events" 
          />
          {isVerified && (
            <ContextPanelLink 
              to={`${basePath}/campus`} 
              icon={uiIcons.schoolOutline} 
              label="Campus Exclusive" 
            />
          )}
          <ContextPanelLink 
            to={`${basePath}/my-events`} 
            icon={uiIcons.calendarCheck} 
            label="My Events" 
          />
        </ContextPanelSection>
      </ContextPanel>

      <Routes>
        <Route 
          path="my-events" 
          element={
            <MyEventsView 
              timeFilter={timeFilter} setTimeFilter={setTimeFilter}
              onRegister={(ev) => setInfoEvent({ ...ev, isRegistered: true })} 
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              isVerified={isVerified}
              myEvents={myEvents}
            />
          } 
        />
        {isVerified && (
          <Route 
            path="/" 
            element={
              <AllEventsView 
                timeFilter={timeFilter} setTimeFilter={setTimeFilter}
                events={events} 
                onRegister={handleInfoEventOpen} 
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
              />
            } 
          />
        )}
        <Route 
          path="public" 
          element={
            <EventsList 
              timeFilter={timeFilter} setTimeFilter={setTimeFilter}
              events={publicEvents} 
              title="PUBLIC EVENTS" 
              subtitle="Events open to external participants and guests." 
              onRegister={handleInfoEventOpen} 
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
            />
          } 
        />
        {isVerified && (
          <Route 
            path="campus" 
            element={
              <EventsList 
                timeFilter={timeFilter} setTimeFilter={setTimeFilter}
                events={campusEvents} 
                title="CAMPUS EXCLUSIVE" 
                subtitle="Internal events exclusively for verified university students." 
                onRegister={handleInfoEventOpen} 
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
              />
            } 
          />
        )}
        <Route path="*" element={<Navigate to={`${basePath}${isVerified ? "" : "/public"}`} replace />} />
      </Routes>

      <EventInfoModal
        event={infoEvent}
        onClose={() => setInfoEvent(null)}
        onRegisterClick={(event) => {
          if (event.checkSchedule) {
            setScheduleEvent(event);
            setInfoEvent(null);
          } else {
            setRegisterEvent(event);
          }
        }}
      />

      <EventScheduleInfoModal
        event={scheduleEvent}
        onClose={() => setScheduleEvent(null)}
      />

      <EventRegistrationModal
        isOpen={!!registerEvent}
        onClose={() => setRegisterEvent(null)}
        event={registerEvent}
        onRegister={handleRegister}
        isExternal={!isVerified}
      />
    </ContextLayout>
  );
};
