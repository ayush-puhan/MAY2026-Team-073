import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { StatCard } from '../../ui/StatCard/StatCard';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { universityAdminApi } from '@api/universityAdminApis/universityAdmin';
import styles from './AdminOverviewHome.module.css';

export const AdminOverviewHome = () => {
  const [stats, setStats] = useState(null);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    (async () => {
      const [statsData, requests] = await Promise.all([
        universityAdminApi.getStats(),
        universityAdminApi.getClubCreationRequests('submitted'),
      ]);
      if (isMounted) {
        setStats(statsData);
        setPendingRequests(requests);
        setLoading(false);
      }
    })();
    return () => { isMounted = false; };
  }, []);

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
        <h2 className={styles.title}>University Administration Overview</h2>
        <p className={styles.subtitle}>Institution-wide governance and compliance at a glance.</p>
      </div>

      <div className={styles.statsGrid}>
        <StatCard title="Active Clubs" value={stats.totalClubs} icon="mdi:account-group-outline" color="var(--primary)" />
        <StatCard title="Total Memberships" value={stats.totalMemberships} icon="mdi:account-multiple-outline" color="var(--sky)" />
        <StatCard title="Active Events" value={stats.activeEvents} icon="mdi:calendar-blank-outline" color="var(--innovation)" />
        <StatCard title="Pending Club Approvals" value={stats.pendingApprovals} icon="mdi:check-decagram-outline" color="var(--campus-orange)" />
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Club Proposals Awaiting Review</h3>
        <DataTable
          columns={[
            { header: 'Proposed Club', accessor: 'proposed_name' },
            { header: 'Category', accessor: 'proposed_category' },
            { header: 'Requested By', accessor: 'requested_by_name' },
            { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
          ]}
          data={pendingRequests}
          emptyIcon="mdi:check-decagram-outline"
          emptyTitle="No pending club proposals"
        />
      </div>
    </div>
  );
};
