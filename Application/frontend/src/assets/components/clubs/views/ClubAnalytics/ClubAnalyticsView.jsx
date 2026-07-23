import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Icon } from '@iconify/react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import { canViewBudget, canManageTasks } from '../../../../../utils/clubPermissions';
import styles from './ClubAnalyticsView.module.css';
import { rewardsIcons, uiIcons, landingIcons } from '../../../../icons/registry';

const CHART_COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

const ClubAnalyticsView = () => {
  const { club, userRole } = useOutletContext();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [club.id]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getClubAnalytics(club.id);
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className={styles.loadingState}>
      <div className={styles.spinner} />
      <p>Loading analytics...</p>
    </div>
  );

  if (!analytics) return null;

  const { summary, membershipGrowth, eventAttendance, expenseDistribution, taskStats, taskTrend, budgetUtilization } = analytics;

  const summaryCards = [
    { label: 'Total Members', value: summary.totalMembers, icon: 'mdi:account-group', colorVar: '--blue' },
    { label: 'Events Organized', value: summary.totalEvents, icon: 'mdi:calendar-check', colorVar: '--achievement' },
    { label: 'Task Completion', value: `${summary.taskCompletionRate}%`, icon: 'mdi:clipboard-check', colorVar: '--purple' },
    { label: 'Budget Used', value: `${budgetUtilization.percentage}%`, icon: 'mdi:wallet', colorVar: '--gold', show: canViewBudget(userRole) }
  ].filter(c => c.show !== false);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h2>Club Analytics</h2>
          <p>Performance metrics & insights for {club.name}</p>
        </div>
      </header>

      {/* Summary Cards */}
      <div className={styles.summaryGrid}>
        {summaryCards.map((card, i) => (
          <div key={i} className={styles.summaryCard}>
            <div className={styles.summaryIcon} style={{ color: `var(${card.colorVar})`, backgroundColor: `color-mix(in srgb, var(${card.colorVar}) 12%, transparent)` }}>
              <Icon icon={card.icon} />
            </div>
            <div className={styles.summaryInfo}>
              <span className={styles.summaryLabel}>{card.label}</span>
              <span className={styles.summaryValue}>{card.value}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className={styles.chartsGrid}>
        {/* Membership Growth */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <Icon icon={rewardsIcons.trendingUp} /> Membership Growth
          </h3>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={membershipGrowth}>
                <defs>
                  <linearGradient id="memberGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} />
                <YAxis tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--foreground)' }} />
                <Area type="monotone" dataKey="members" stroke="#3b82f6" strokeWidth={2} fill="url(#memberGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Event Attendance */}
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>
            <Icon icon={uiIcons.chartBar} /> Event Attendance
          </h3>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={eventAttendance}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--foreground)' }} />
                <Legend />
                <Bar dataKey="registered" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Registered" />
                <Bar dataKey="attended" fill="#10b981" radius={[4, 4, 0, 0]} name="Attended" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Budget Pie Chart - only for finance roles */}
        {canViewBudget(userRole) && expenseDistribution.length > 0 && (
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>
              <Icon icon={uiIcons.chartDonut} /> Budget Distribution
            </h3>
            <div className={styles.chartWrapper}>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={expenseDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {expenseDistribution.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--foreground)' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Task Trend */}
        {canManageTasks(userRole) && (
          <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>
              <Icon icon={uiIcons.clipboardTextClock} /> Task Trend
            </h3>
            <div className={styles.chartWrapper}>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={taskTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} />
                  <YAxis tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--foreground)' }} />
                  <Legend />
                  <Bar dataKey="assigned" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Assigned" />
                  <Bar dataKey="completed" fill="#10b981" radius={[4, 4, 0, 0]} name="Completed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* AI Insights Coming Soon */}
      <div className={styles.aiInsights}>
        <div className={styles.aiIcon}>
          <Icon icon={landingIcons.robotOutline} />
        </div>
        <div className={styles.aiContent}>
          <h3>AI-Powered Insights</h3>
          <p>Smart recommendations for club growth, event optimization, and member engagement are coming soon.</p>
          <span className={styles.comingBadge}>Coming Soon</span>
        </div>
      </div>
    </div>
  );
};

export default ClubAnalyticsView;
