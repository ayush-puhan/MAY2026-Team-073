import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

import { FacultyDashboardHome } from '../../../assets/components/facultyAdvisor/FacultyDashboardHome/FacultyDashboardHome';
import { AdvisedClubs } from '../../../assets/components/facultyAdvisor/AdvisedClubs/AdvisedClubs';
import { EventApprovals } from '../../../assets/components/facultyAdvisor/EventApprovals/EventApprovals';
import { FacultyReports } from '../../../assets/components/facultyAdvisor/FacultyReports/FacultyReports';
import { AnnouncementCenter } from '../../../assets/components/announcements/AnnouncementCenter/AnnouncementCenter';
import { GlobalCalendar } from '../../../assets/components/calendar/GlobalCalendar/GlobalCalendar';
import { Helpdesk } from '../../../assets/components/student/Helpdesk/Helpdesk';
import styles from './FacultyAdvisorDashboard.module.css';

export const FacultyAdvisorDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  return (
    <DashboardLayout title="Faculty Advisor Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div style={{ width: '100%' }}>
        <Routes>
          <Route path="/" element={<FacultyDashboardHome />} />
          <Route path="clubs/*" element={<AdvisedClubs />} />
          <Route path="events/*" element={<EventApprovals />} />
          <Route path="reports/*" element={<FacultyReports />} />
          <Route path="announcements/*" element={<AnnouncementCenter />} />
          <Route path="calendar/*" element={<GlobalCalendar />} />
          <Route path="helpdesk/*" element={<Helpdesk />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};
