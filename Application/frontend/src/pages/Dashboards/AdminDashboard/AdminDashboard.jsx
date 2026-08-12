import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

// Import Admin Modules
import { DashboardHome } from '../../../assets/components/admin/DashboardHome/DashboardHome';
import { UserManagement } from '../../../assets/components/admin/UserManagement/UserManagement';
import { RoleDirectory } from '../../../assets/components/admin/RoleDirectory/RoleDirectory';
import { ReportsAnalytics } from '../../../assets/components/admin/ReportsAnalytics/ReportsAnalytics';
import { PlatformSettings } from '../../../assets/components/admin/PlatformSettings/PlatformSettings';
import { SupportManagement } from '../../../assets/components/admin/SupportManagement/SupportManagement';
import { AuditLogs } from '../../../assets/components/admin/AuditLogs/AuditLogs';
import { AnnouncementCenter } from '../../../assets/components/announcements/AnnouncementCenter/AnnouncementCenter';
import { GlobalCalendar } from '../../../assets/components/calendar/GlobalCalendar/GlobalCalendar';
import { NotificationsView } from '../../../assets/components/notifications/NotificationsView/NotificationsView';

import styles from './AdminDashboard.module.css';

export const AdminDashboard = () => {
  const { user } = useSession();
  
  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  return (
    <DashboardLayout title="System Administration" user={user} sidebarLinks={sidebarLinks}>
      <div className={styles.adminContainer}>
        <Routes>
          <Route path="/" element={<DashboardHome />} />
          <Route path="users/*" element={<UserManagement />} />
          <Route path="roles/*" element={<RoleDirectory />} />
          <Route path="reports/*" element={<ReportsAnalytics />} />
          <Route path="settings/*" element={<PlatformSettings />} />
          <Route path="support/*" element={<SupportManagement />} />
          <Route path="audit/*" element={<AuditLogs />} />
          <Route path="announcements/*" element={<AnnouncementCenter />} />
          <Route path="calendar/*" element={<GlobalCalendar />} />
          <Route path="notifications" element={<NotificationsView />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};

