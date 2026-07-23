import React, { useState, useEffect } from 'react';
import { Icon } from '@iconify/react';
import { StatCard } from '../../ui/StatCard/StatCard';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { universityAdminApi } from '@api/universityAdminApis/universityAdmin';
import styles from './AdminOverviewHome.module.css';
import { uiIcons, dashboardIcons } from '../../../icons/registry';

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
        <Icon icon={uiIcons.loading} className="animate-spin" width="32" />
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
        <StatCard title="Active Clubs" value={stats.totalClubs} icon={dashboardIcons.accountGroupOutline} color="var(--primary)" />
        <StatCard title="Total Memberships" value={stats.totalMemberships} icon={dashboardIcons.accountMultipleOutline} color="var(--sky)" />
        <StatCard title="Active Events" value={stats.activeEvents} icon={dashboardIcons.calendarBlankOutline} color="var(--innovation)" />
        <StatCard title="Pending Club Approvals" value={stats.pendingApprovals} icon={dashboardIcons.checkDecagramOutline} color="var(--campus-orange)" />
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
          emptyIcon={dashboardIcons.checkDecagramOutline}
          emptyTitle="No pending club proposals"
        />
      </div>
    </div>
  );
};
