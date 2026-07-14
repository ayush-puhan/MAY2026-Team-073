import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';

import { useSession } from '../../../context/SessionContext';

export const UniversityAdminDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser('University Admin');

  return (
    <DashboardLayout title="University Admin Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div>
        <h2 style={{ color: 'var(--foreground)', marginBottom: '1rem' }}>University Overview</h2>
        <p style={{ color: 'var(--muted-foreground)' }}>Manage student affairs, club approvals, and academic events here.</p>
      </div>
    </DashboardLayout>
  );
};
