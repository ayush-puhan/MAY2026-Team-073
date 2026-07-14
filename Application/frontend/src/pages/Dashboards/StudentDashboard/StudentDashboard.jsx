import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';

import { useSession } from '../../../context/SessionContext';

export const StudentDashboard = () => {
  const { user } = useSession();
  
  // Fallback in case user is not loaded yet
  if (!user) return null;

  const sidebarLinks = getNavForUser(user.role);

  return (
    <DashboardLayout title="Student Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div>
        <h2 style={{ color: 'var(--foreground)', marginBottom: '1rem' }}>Welcome back, Alex!</h2>
        <p style={{ color: 'var(--muted-foreground)' }}>This is the student dashboard. More features coming soon.</p>
      </div>
    </DashboardLayout>
  );
};
