import { useEffect, useRef } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../../../assets/components/dashboard/DashboardLayout/DashboardLayout';
import { getNavForUser } from '../../../config/navigation';
import { useSession } from '../../../context/SessionContext';
import { useToast } from '../../../context/ToastContext';
import { Helpdesk } from '../../../assets/components/student/Helpdesk/Helpdesk';
import styles from './StudentDashboard.module.css';

export const StudentDashboard = () => {
  const { user } = useSession();
  const { showInfo } = useToast();
  const hasToasted = useRef(false);
  
  useEffect(() => {
    if (user && !hasToasted.current) {
      const isVerified = user.student_profile?.is_verified;
      const hasOptedOut = user.browse_public_only || user.preferences?.browse_public_only;
      
      if (!isVerified && !hasOptedOut) {
        hasToasted.current = true;
        const timer = setTimeout(() => {
          showInfo("Verify your university campus email to get full access to clubs and events.", 6000);
        }, 2000);
        return () => clearTimeout(timer);
      }
    }
  }, [user, showInfo]);

  if (!user) return null;

  const sidebarLinks = getNavForUser(user);

  const mockEvents = [
    { id: 1, title: 'Inter-College Chess Championship', date: '2026-08-15', location: 'Main Hall', type: 'Open to All' },
    { id: 2, title: 'Tech Startup Pitch Night', date: '2026-08-18', location: 'Auditorium', type: 'Open to All' },
    { id: 3, title: 'Campus Photography Walk', date: '2026-08-20', location: 'Campus Grounds', type: 'Open to All' }
  ];

  return (
    <DashboardLayout title="Student Dashboard" user={user} sidebarLinks={sidebarLinks}>
      <div className={styles.container} style={{ width: '100%' }}>
        <Routes>
          <Route path="/" element={
            <>
              <div className={styles.welcomeSection}>
                <h2 className={styles.welcomeTitle}>Welcome back, {user.full_name?.split(' ')[0] || 'Student'}!</h2>
                <p className={styles.welcomeDesc}>Here is a quick overview of what's happening around campus.</p>
              </div>

              <div className={styles.dashboardGrid}>
                <div className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>Upcoming Events (Open to All)</h3>
                  </div>
                  <div className={styles.cardContent}>
                    {mockEvents.map(ev => (
                      <div key={ev.id} className={styles.eventItem}>
                        <div className={styles.eventInfo}>
                          <strong>{ev.title}</strong>
                          <span>{ev.date} • {ev.location}</span>
                        </div>
                        <span className={styles.badge}>{ev.type}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3>My Clubs</h3>
                  </div>
                  <div className={styles.cardContent}>
                    <p className={styles.emptyText}>You haven't joined any clubs yet. Head over to Discover to find communities!</p>
                  </div>
                </div>
              </div>
            </>
          } />
          
          <Route path="helpdesk/*" element={<Helpdesk />} />
          
          <Route path="*" element={<Navigate to="" replace />} />
        </Routes>
      </div>
    </DashboardLayout>
  );
};



