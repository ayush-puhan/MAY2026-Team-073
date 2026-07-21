import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { eventsApi } from '../../../../api';
import { useSession } from '../../../../context/SessionContext';
import { EventCard } from '../../ui/EventCard/EventCard';
import { EventInfoModal } from '../../ui/EventInfoModal/EventInfoModal';
import { EventRegistrationModal } from '../../ui/EventRegistrationModal/EventRegistrationModal';
import { useToast } from '../../../../context/ToastContext';
import { ContextLayout } from '../../ui/ContextLayout/ContextLayout';
import { ContextPanel, ContextPanelSection, ContextPanelLink } from '../../ui/ContextLayout/ContextPanel';
import { SecondaryHeader } from '../../ui/SecondaryHeader/SecondaryHeader';
import layoutStyles from '../../ui/ContextLayout/ContextLayout.module.css';
import styles from './EventsHub.module.css';

const DiscoverHeader = ({ title, subtitle, searchQuery, setSearchQuery, activeTab, onTabChange }) => {
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

const EventsList = ({ events, title, subtitle, onRegister, searchQuery, setSearchQuery }) => {
  const [activeTab, setActiveTab] = useState('all');
  
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
  
  const finalEvents = filterEventsByTab(searchFiltered, activeTab);

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
        />
        
        <h2 className={styles.sectionTitle} style={{ marginBottom: '1.5rem' }}>Upcoming</h2>
        
        <div className={styles.grid}>
          {finalEvents.length > 0 ? (
            finalEvents.map(ev => (
              <EventCard 
                key={ev.id}
                title={ev.title}
                subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
                university={ev.club?.university?.name || ev.university || "IIT Delhi"}
                rightElement={ev.status}
                bannerKeyword={ev.banner || ev.category?.toLowerCase()}
                onClick={() => onRegister(ev)}
              />
            ))
          ) : (
            <div className={styles.emptyState}>
              <Icon icon="mdi:calendar-search" />
              <p>No events found in this category.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const AllEventsView = ({ events, onRegister, searchQuery, setSearchQuery }) => {
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

  const campusEvents = tabFiltered.filter(ev => !isPublicEvent(ev));
  const publicEvents = tabFiltered.filter(isPublicEvent);

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent} style={{ paddingTop: '0' }}>
        <DiscoverHeader 
          title="DISCOVER CAMPUS EVENTS" 
          subtitle="From hackathons to music festivals, there's a place for you." 
          searchQuery={searchQuery} 
          setSearchQuery={setSearchQuery} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        
        <div className={styles.splitLayout}>
          <div className={styles.categorySection}>
            <h2 className={styles.sectionTitle}>
              <Icon icon="mdi:school-outline" style={{ color: 'var(--primary)' }} /> Campus Exclusive
            </h2>
            <div className={styles.grid}>
              {campusEvents.length > 0 ? (
                campusEvents.map(ev => (
                  <EventCard 
                    key={ev.id}
                    title={ev.title}
                    subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
                    university={ev.club?.university?.name || ev.university || "IIT Delhi"}
                    rightElement={ev.status}
                    bannerKeyword={ev.banner || ev.category?.toLowerCase()}
                    onClick={() => onRegister(ev)}
                  />
                ))
              ) : (
                <p className={styles.noResultsText}>No campus events found.</p>
              )}
            </div>
          </div>
          
          <div className={styles.categorySection}>
            <h2 className={styles.sectionTitle}>
              <Icon icon="mdi:earth" style={{ color: 'var(--gold)' }} /> Public Events
            </h2>
            <div className={styles.grid}>
              {publicEvents.length > 0 ? (
                publicEvents.map(ev => (
                  <EventCard 
                    key={ev.id}
                    title={ev.title}
                    subtitle={`${ev.capacity ? ev.capacity + ' seats • ' : ''}${ev.venue || 'TBA'}`}
                    university={ev.club?.university?.name || ev.university || "IIT Delhi"}
                    rightElement={ev.status}
                    bannerKeyword={ev.banner || ev.category?.toLowerCase()}
                    onClick={() => onRegister(ev)}
                  />
                ))
              ) : (
                <p className={styles.noResultsText}>No public events found.</p>
              )}
            </div>
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
  const [infoEvent, setInfoEvent] = useState(null);
  const [registerEvent, setRegisterEvent] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const isVerified = user?.student_profile?.is_verified === 1 || user?.student_profile?.is_verified === true;
  const isPublicEvent = (ev) => ev.is_public === true || ev.is_public === 1 || ev.is_public === "1";

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await eventsApi.getAllEvents();
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
  }, [isVerified]);

  const handleRegister = async (formData) => {
    try {
      await eventsApi.registerForEvent(registerEvent.id, user.id, !isVerified, formData);
      addToast({ title: 'Success', message: `Registered for ${registerEvent?.title}`, type: 'success' });
      setRegisterEvent(null);
      setInfoEvent(null);
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
              icon="mdi:compass-outline" 
              label="All Events" 
            />
          )}
          <ContextPanelLink 
            to={`${basePath}/public`} 
            icon="mdi:earth" 
            label="Public Events" 
          />
          {isVerified && (
            <ContextPanelLink 
              to={`${basePath}/campus`} 
              icon="mdi:school-outline" 
              label="Campus Exclusive" 
            />
          )}
        </ContextPanelSection>
      </ContextPanel>

      <Routes>
        {isVerified && (
          <Route 
            path="/" 
            element={
              <AllEventsView 
                events={events} 
                onRegister={setInfoEvent} 
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
              events={publicEvents} 
              title="PUBLIC EVENTS" 
              subtitle="Events open to external participants and guests." 
              onRegister={setInfoEvent} 
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
                events={campusEvents} 
                title="CAMPUS EXCLUSIVE" 
                subtitle="Internal events exclusively for verified university students." 
                onRegister={setInfoEvent} 
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
        onRegisterClick={(event) => setRegisterEvent(event)}
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
