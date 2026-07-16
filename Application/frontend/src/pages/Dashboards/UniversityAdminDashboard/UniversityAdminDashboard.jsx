import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

import { AdminOverviewHome } from '../../../assets/components/universityAdmin/AdminOverviewHome/AdminOverviewHome';
import { ClubApprovalQueue } from '../../../assets/components/universityAdmin/ClubApprovalQueue/ClubApprovalQueue';
import { UniversityAnalytics } from '../../../assets/components/universityAdmin/UniversityAnalytics/UniversityAnalytics';
import { EventOversight } from '../../../assets/components/universityAdmin/EventOversight/EventOversight';
import { AnnouncementCenter } from '../../../assets/components/universityAdmin/AnnouncementCenter/AnnouncementCenter';
import { DashboardSettings } from '../../../assets/components/dashboard/DashboardSettings/DashboardSettings';

import styles from './UniversityAdminDashboard.module.css';

export const UniversityAdminDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser(user.role);

  return (
    <DashboardLayout title="University Admin Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div className={styles.container}>
        <Routes>
          <Route path="/" element={<AdminOverviewHome />} />
          <Route path="approvals/*" element={<ClubApprovalQueue />} />
          <Route path="reports/*" element={<UniversityAnalytics />} />
          <Route path="events/*" element={<EventOversight />} />
          <Route path="announcements/*" element={<AnnouncementCenter />} />
          <Route path="settings/*" element={<DashboardSettings />} />
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};
