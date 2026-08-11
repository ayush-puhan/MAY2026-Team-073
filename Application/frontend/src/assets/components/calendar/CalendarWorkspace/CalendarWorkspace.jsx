import { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer, Views } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import CustomEventBlock from '../CustomEventBlock/CustomEventBlock';
import EventDetailsDrawer from '../EventDetailsDrawer/EventDetailsDrawer';
import styles from './CalendarWorkspace.module.css';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

const CalendarWorkspace = ({ events, loading, user, filters, setFilters }) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const view = filters?.calendarView || Views.WEEK;
  const [date, setDate] = useState(new Date());
  
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 768;
      if (mobile !== isMobile) {
        setIsMobile(mobile);
        if (mobile && (view === Views.MONTH || view === Views.WEEK || view === Views.DAY)) {
          setFilters(prev => ({ ...prev, calendarView: Views.AGENDA }));
        } else if (!mobile && view === Views.AGENDA) {
          setFilters(prev => ({ ...prev, calendarView: Views.MONTH }));
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isMobile, view, setFilters]);
  
  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const handleSelectEvent = (event) => {
    setSelectedEvent(event);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setSelectedEvent(null);
  };

  return (
    <div className={styles.workspaceContainer}>
      <div className={styles.calendarHeader}>
        <h1>Your Calendar</h1>
      </div>

      <div className={styles.calendarWrapper}>
        {loading && events.length === 0 && (
          <div className={styles.loadingOverlay}>
            <div className={styles.spinner}></div>
          </div>
        )}
        
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          view={view}
          views={['month', 'week', 'day', 'agenda']}
          date={date}
          onView={(newView) => setFilters(prev => ({ ...prev, calendarView: newView }))}
          onNavigate={(newDate) => setDate(newDate)}
          onSelectEvent={handleSelectEvent}
          popup
          selectable
          components={{
            event: CustomEventBlock
          }}
          eventPropGetter={(event) => {
            const backgroundColor = event.color || 'var(--primary)';
            return {
              style: {
                backgroundColor,
                opacity: 0.9,
                color: '#fff',
                border: 'none'
              }
            };
          }}
        />
      </div>

      {drawerOpen && selectedEvent && (
        <EventDetailsDrawer 
          event={selectedEvent} 
          onClose={closeDrawer} 
          user={user} 
        />
      )}
    </div>
  );
};

export default CalendarWorkspace;

