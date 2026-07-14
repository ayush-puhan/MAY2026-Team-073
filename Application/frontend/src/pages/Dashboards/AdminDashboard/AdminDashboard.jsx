import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';

import { useSession } from '../../../context/SessionContext';

export const AdminDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser(user.role);

  return (
    <DashboardLayout title="Admin Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div>
        <h2 style={{ color: 'var(--foreground)', marginBottom: '1rem' }}>System Admin Overview</h2>
        <p style={{ color: 'var(--muted-foreground)' }}>This is the dashboard for system administrators. Manage the platform's core settings here.</p>
      </div>
    </DashboardLayout>
  );
};
