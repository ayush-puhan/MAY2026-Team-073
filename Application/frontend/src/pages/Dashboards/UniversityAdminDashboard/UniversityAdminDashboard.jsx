import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

import { SupportManagement } from '../../../assets/components/admin/SupportManagement/SupportManagement';
import { Helpdesk } from '../../../assets/components/student/Helpdesk/Helpdesk';
import { AnnouncementCenter } from '../../../assets/components/announcements/AnnouncementCenter/AnnouncementCenter';

import { AdminOverviewHome } from '../../../assets/components/universityAdmin/AdminOverviewHome/AdminOverviewHome';
import { ClubApprovalQueue } from '../../../assets/components/universityAdmin/ClubApprovalQueue/ClubApprovalQueue';
import { EventOversight } from '../../../assets/components/universityAdmin/EventOversight/EventOversight';
import { UniversityAnalytics } from '../../../assets/components/universityAdmin/UniversityAnalytics/UniversityAnalytics';

import { GlobalCalendar } from '../../../assets/components/calendar/GlobalCalendar/GlobalCalendar';
import { EmergencyDashboard } from '../../../assets/components/universityAdmin/EmergencyDashboard/EmergencyDashboard';

export const UniversityAdminDashboard = () => {
  const { user } = useSession();
  
  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  return (
    <DashboardLayout title="University Admin Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div style={{ width: '100%' }}>
        <Routes>
          <Route path="/" element={<AdminOverviewHome />} />
          <Route path="helpdesk/*" element={<Helpdesk />} />
          <Route path="support/*" element={<SupportManagement />} />
          <Route path="approvals/*" element={<ClubApprovalQueue />} />
          <Route path="reports/*" element={<UniversityAnalytics />} />
          
          <Route path="announcements/*" element={<AnnouncementCenter />} />
          
          <Route path="emergencies/*" element={<EmergencyDashboard />} />
          <Route path="calendar/*" element={<GlobalCalendar />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};





