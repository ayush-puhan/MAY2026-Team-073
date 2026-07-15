import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { StatCard } from '../../ui/StatCard/StatCard';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { facultyAdvisorApi } from '../../../../api/facultyAdvisor.api';
import { useSession } from '../../../../context/SessionContext';
import styles from './FacultyDashboardHome.module.css';

export const FacultyDashboardHome = () => {
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
          facultyAdvisorApi.getEvents(user.id, 'pending'),
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
        <Icon icon="mdi:loading" className="animate-spin" width="32" />
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
        <StatCard title="Advised Clubs" value={stats.advisedClubs} icon="mdi:account-group-outline" color="var(--primary)" />
        <StatCard title="Total Members" value={stats.totalMembers} icon="mdi:account-multiple-outline" color="var(--sky)" />
        <StatCard title="Pending Event Approvals" value={stats.pendingEvents} icon="mdi:calendar-check-outline" color="var(--campus-orange)" />
        <StatCard title="Pending Expense Approvals" value={stats.pendingExpenses} icon="mdi:cash-multiple" color="var(--achievement)" />
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Events Awaiting Your Approval</h3>
        <DataTable
          columns={[
            { header: 'Event', accessor: 'title' },
            { header: 'Club', accessor: 'club_name' },
            { header: 'Date', cell: (row) => new Date(row.start_at).toLocaleDateString() },
            { header: 'Status', cell: (row) => <StatusBadge status={row.approval_status} /> },
          ]}
          data={pendingEvents}
          emptyIcon="mdi:calendar-check-outline"
          emptyTitle="No events awaiting approval"
          emptyDesc="New event submissions from your advised clubs will show up here."
        />
      </div>
    </div>
  );
};
