import { useState, useEffect } from 'react';
import { adminApi } from '@api/adminApis/admin';
import { StatCard } from '../../ui/StatCard/StatCard';
import { DataTable } from '../../ui/DataTable/DataTable';
import { StatusBadge } from '../../ui/StatusBadge/StatusBadge';
import { Icon } from '@iconify/react';
import { adminIcons, uiIcons } from '../../../icons/registry';
import styles from './DashboardHome.module.css';

export const DashboardHome = () => {
  const [realStats, setRealStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalClubs: 0,
    totalEvents: 0,
    openTickets: 0
  });
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, logsData] = await Promise.all([
          adminApi.getStats(),
          adminApi.getAuditLogs(5)
        ]);
        setRealStats(statsData);
        setLogs(logsData);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const columns = [
    { header: 'Action', accessor: 'action' },
    { header: 'Entity Type', accessor: 'entity_type' },
    { header: 'Details', accessor: 'details' },
    { 
      header: 'Date', 
      cell: (row) => new Date(row.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
    }
  ];

  if (loading) {
    return <div className={styles.loading}><Icon icon={uiIcons.loading} className="spin" width="32" /></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>System Overview</h2>
        <p className={styles.subtitle}>A high-level view of ClubConnect platform metrics.</p>
      </div>

      <div className={styles.statsGrid}>
        <StatCard 
          title="Total Users" 
          value={realStats.totalUsers} 
          icon={adminIcons.statsUsers}
          trend={realStats.userTrend || 0}
          trendLabel="vs last month"
          color="var(--primary)"
        />
        <StatCard 
          title="Active Clubs" 
          value={realStats.totalClubs} 
          icon={adminIcons.statsClubs}
          color="var(--success)"
        />
        <StatCard 
          title="Events Hosted" 
          value={realStats.totalEvents} 
          icon={adminIcons.statsEvents}
          trend={realStats.eventsTrend || 0}
          trendLabel="this semester"
          color="var(--secondary)"
        />
        <StatCard 
          title="Open Tickets" 
          value={realStats.openTickets} 
          icon={adminIcons.statsTickets}
          trend={realStats.ticketsTrend || 0}
          trendLabel="vs last week"
          color="var(--warning)"
        />
      </div>

      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Recent System Activity</h3>
        </div>
        <DataTable 
          columns={columns} 
          data={logs} 
          emptyTitle="No activity found"
          emptyDesc="No recent system actions have been logged."
        />
      </div>
    </div>
  );
};
