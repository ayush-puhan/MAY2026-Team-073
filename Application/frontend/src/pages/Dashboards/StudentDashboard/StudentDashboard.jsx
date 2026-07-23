import React, { useEffect, useState, useRef } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';
import { Helpdesk } from '../../../assets/components/student/Helpdesk/Helpdesk';
import { AnnouncementCenter } from '../../../assets/components/announcements/AnnouncementCenter/AnnouncementCenter';
import { GlobalCalendar } from '../../../assets/components/calendar/GlobalCalendar/GlobalCalendar';
import { RewardsHub } from './RewardsHub';
import { getRandomGreeting } from '../../../config/greetings';
import { eventsApi } from '../../../api';
import { VerifiedHome } from './VerifiedHome/VerifiedHome';
import { GuestHome } from './GuestHome/GuestHome';
import { EventsHub } from '../../../assets/components/events/EventsHub/EventsHub';
import { ClubsHub } from '../../../assets/components/clubs/ClubsHub/ClubsHub';
import styles from './StudentDashboard.module.css';

export const StudentDashboard = () => {
  const { user } = useSession();
  const location = useLocation();
  const [publicEvents, setPublicEvents] = useState([]);
  
  const isVerified = user?.student_profile?.is_verified === 1 || user?.student_profile?.is_verified === true;
  const hasOptedOut = user?.browse_public_only || user?.preferences?.browse_public_only;
  
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await eventsApi.getAllEvents();
        let eventsToShow;
        if (!isVerified) {
          // Guest users: only show public events that allow external participants
          const guestVisible = data.filter(e => 
            (e.is_public === true || e.is_public === 1 || e.is_public === "1") &&
            (e.requires_external_participants === true || e.requires_external_participants === 1 || e.requires_external_participants === "1")
          );
          eventsToShow = guestVisible;
        } else {
          const publicOnly = data.filter(e => e.is_public === true || e.is_public === 1 || e.is_public === "1");
          eventsToShow = publicOnly.length > 0 ? publicOnly : data;
        }
        setPublicEvents(eventsToShow.slice(0, 6));
      } catch (err) {
        console.error("Failed to load events", err);
      }
    };
    fetchEvents();
  }, [isVerified]);

  const greetingQuote = useRef(getRandomGreeting());

  if (!user) return null;

  const sidebarLinks = getNavForUser(user);
  const noPadding = location.pathname.includes('/events') || location.pathname.includes('/rewards') || location.pathname.includes('/calendar') || location.pathname.includes('/clubs');

  return (
    <DashboardLayout title="Campus Home" user={user} sidebarLinks={sidebarLinks} noPadding={noPadding}>
      <div className={styles.homeContainer}>
        <Routes>
          <Route path="/" element={
            isVerified 
              ? <VerifiedHome user={user} quote={greetingQuote.current} events={publicEvents} />
              : <GuestHome quote={greetingQuote.current} publicEvents={publicEvents} hasOptedOut={hasOptedOut} />
          } />
          
          <Route path="helpdesk/*" element={<Helpdesk />} />
          <Route path="announcements/*" element={<AnnouncementCenter />} />
          <Route path="calendar/*" element={<GlobalCalendar />} />
          <Route path="events/*" element={<EventsHub />} />
          <Route path="clubs/*" element={<ClubsHub />} />
          <Route path="rewards/*" element={<RewardsHub />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};
