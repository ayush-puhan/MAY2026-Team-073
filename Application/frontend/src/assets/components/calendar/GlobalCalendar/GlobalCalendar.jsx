import React, { useState, useEffect } from 'react';
import { useSession } from '../../../../context/SessionContext';
import { calendarApi } from '../../../../api';
import CalendarContextPanel from '../CalendarContextPanel/CalendarContextPanel';
import CalendarWorkspace from '../CalendarWorkspace/CalendarWorkspace';
import styles from './GlobalCalendar.module.css';

export const GlobalCalendar = () => {
  const { user } = useSession();
  
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters state
  const [filters, setFilters] = useState({
    show_public: false,
    university_id: '',
    club_id: '',
    searchQuery: '',
    calendarView: window.innerWidth <= 768 ? 'day' : 'week'
  });

  // Fetch events when filters or user changes
  useEffect(() => {
    if (!user) return;
    
    const fetchEvents = async () => {
      setLoading(true);
      try {
        const data = await calendarApi.getCalendarEvents(user.id, filters);
        setEvents(data);
      } catch (err) {
        console.error("Failed to load calendar events", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchEvents();
  }, [user, filters.show_public, filters.university_id, filters.club_id]);

  // Client-side search filtering (since search is fast enough to do locally on the fetched set)
  const displayedEvents = events.filter(ev => {
    if (!filters.searchQuery) return true;
    const q = filters.searchQuery.toLowerCase();
    return (
      ev.sessionTitle?.toLowerCase().includes(q) ||
      ev.eventTitle?.toLowerCase().includes(q) ||
      ev.clubName?.toLowerCase().includes(q)
    );
  });

  return (
    <div className={styles.calendarModule}>
      <CalendarContextPanel 
        filters={filters} 
        setFilters={setFilters} 
        user={user} 
      />
      
      <div className={styles.workspace}>
        <CalendarWorkspace 
          events={displayedEvents} 
          loading={loading}
          user={user}
          filters={filters}
          setFilters={setFilters}
        />
      </div>
    </div>
  );
};

