import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';

// Re-use SupportManagement from admin components
import { SupportManagement } from '../../../assets/components/admin/SupportManagement/SupportManagement';

export const UniversityAdminDashboard = () => {
  const { user } = useSession();
  
  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  return (
    <DashboardLayout title="University Admin Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div style={{ width: '100%' }}>
        <Routes>
          <Route path="/" element={
            <div>
              <h2 style={{ color: 'var(--foreground)', marginBottom: '1rem' }}>University Overview</h2>
              <p style={{ color: 'var(--muted-foreground)' }}>Manage student affairs, club approvals, and academic events here.</p>
            </div>
          } />
          
          <Route path="support/*" element={<SupportManagement />} />
          
          {/* Redirect unbuilt routes back to overview for now */}
          <Route path="approvals/*" element={<Navigate to="" replace />} />
          <Route path="reports/*" element={<Navigate to="" replace />} />
          <Route path="events/*" element={<Navigate to="" replace />} />
          <Route path="settings/*" element={<Navigate to="" replace />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};

