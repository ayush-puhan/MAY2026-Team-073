import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';

import { useSession } from '../../../context/SessionContext';

export const FacultyAdvisorDashboard = () => {
  const { user } = useSession();
  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  return (
    <DashboardLayout title="Faculty Advisor Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div>
        <h2 style={{ color: 'var(--foreground)', marginBottom: '1rem' }}>Faculty Advisor Portal</h2>
        <p style={{ color: 'var(--muted-foreground)' }}>This is the faculty advisor dashboard. More features coming soon.</p>
      </div>
    </DashboardLayout>
  );
};

