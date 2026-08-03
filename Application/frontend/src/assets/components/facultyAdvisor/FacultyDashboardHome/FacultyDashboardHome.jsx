import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { StatCard } from '../../ui/StatCard/StatCard';
import { EventCard } from '../../ui/EventCard/EventCard';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { facultyAdvisorApi } from '@api/facultyAdvisorApis/facultyAdvisor';
import { useSession } from '../../../../context/SessionContext';
import styles from './FacultyDashboardHome.module.css';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

export const FacultyDashboardHome = () => {
  const navigate = useNavigate();
  const { user } = useSession();
  const [stats, setStats] = useState(null);
  const [pendingEvents, setPendingEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const [statsData, events] = await Promise.all([
          facultyAdvisorApi.getStats(user.id),
          facultyAdvisorApi.getEvents(user.id, 'pending_approval'),
        ]);
        if (isMounted) {
          setStats(statsData);
          setPendingEvents(events);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    })();
    return () => { isMounted = false; };
  }, [user.id]);

  if (loading) {
    return (
      <div className={styles.loading}>
        <Icon icon={uiIcons.loading} className="animate-spin" width="32" />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Faculty Advisor Overview</h2>
        <p className={styles.subtitle}>Supervise your clubs' operations, events, and finances.</p>
      </div>

      <div className={styles.statsGrid}>
        <StatCard title="Advised Clubs" value={stats.advisedClubs} icon={dashboardIcons.accountGroupOutline} color="var(--primary)" onClick={() => navigate('/faculty-advisor-dashboard/clubs')} />
        <StatCard title="Total Members" value={stats.totalMembers} icon={dashboardIcons.accountMultipleOutline} color="var(--sky)" onClick={() => navigate('/faculty-advisor-dashboard/clubs')} />
        <StatCard title="Pending Event Approvals" value={stats.pendingEvents} icon={dashboardIcons.calendarCheckOutline} color="var(--campus-orange)" onClick={() => navigate('/faculty-advisor-dashboard/events')} />
        <StatCard title="Pending Expense Approvals" value={stats.pendingExpenses} icon={dashboardIcons.cashMultiple} color="var(--achievement)" onClick={() => navigate('/faculty-advisor-dashboard/reports')} />
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Events Awaiting Your Approval</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
          {pendingEvents.length === 0 ? (
            <p className={styles.emptyText} style={{ gridColumn: '1 / -1', color: 'var(--muted-foreground)' }}>
              No events awaiting approval. New event submissions from your advised clubs will show up here.
            </p>
          ) : (
            pendingEvents.map(ev => (
              <EventCard
                key={ev.id}
                title={ev.title}
                subtitle={`${ev.club_name} • ${new Date(ev.start_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}`}
                icon={uiIcons.calendarAlert}
                color="var(--campus-orange)"
                bannerKeyword={ev.bannerKeyword}
                onClick={() => navigate('/faculty-advisor-dashboard/events')}
                rightElement={
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--campus-orange)' }}>Needs Review</span>
                }
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};
