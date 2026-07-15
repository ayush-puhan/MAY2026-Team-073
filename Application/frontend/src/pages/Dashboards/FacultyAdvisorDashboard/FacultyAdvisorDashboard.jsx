import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

import { FacultyDashboardHome } from '../../../assets/components/facultyAdvisor/FacultyDashboardHome/FacultyDashboardHome';
import { AdvisedClubs } from '../../../assets/components/facultyAdvisor/AdvisedClubs/AdvisedClubs';
import { EventApprovals } from '../../../assets/components/facultyAdvisor/EventApprovals/EventApprovals';
import { FacultyReports } from '../../../assets/components/facultyAdvisor/FacultyReports/FacultyReports';
import { CommunicationCenter } from '../../../assets/components/facultyAdvisor/CommunicationCenter/CommunicationCenter';
import { DashboardSettings } from '../../../assets/components/dashboard/DashboardSettings/DashboardSettings';

import styles from './FacultyAdvisorDashboard.module.css';

export const FacultyAdvisorDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser(user.role);

  return (
    <DashboardLayout title="Faculty Advisor Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div className={styles.container}>
        <Routes>
          <Route path="/" element={<FacultyDashboardHome />} />
          <Route path="clubs/*" element={<AdvisedClubs />} />
          <Route path="events/*" element={<EventApprovals />} />
          <Route path="reports/*" element={<FacultyReports />} />
          <Route path="messages/*" element={<CommunicationCenter />} />
          <Route path="settings/*" element={<DashboardSettings />} />
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};
