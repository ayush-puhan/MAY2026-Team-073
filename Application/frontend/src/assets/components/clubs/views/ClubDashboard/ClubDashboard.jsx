import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Icon } from '@iconify/react';
import styles from './ClubDashboard.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import {
  canManageMembers,
  canPostAnnouncement,
  canManageEvents,
  canManageTasks,
  getRoleLabel,
  getRoleIcon,
  getRoleColor
} from '../../../../../utils/clubPermissions';
import { useToast } from '../../../../../context/ToastContext';
import { StatCard } from '../../../ui/StatCard/StatCard';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { uiIcons, dashboardIcons } from '../../../../icons/registry';

export const ClubDashboard = ({ club, userRole, membersCount = 0, pendingCount = 0, tasksCount = 0 }) => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const basePath = location.pathname.replace(/\/dashboard$/, '');

  const [eventsCount, setEventsCount] = useState(0);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    clubsApi.getClubEvents(club.id).then(events => {
      const upcoming = events.filter(e => new Date(e.start_at) > new Date());
      setEventsCount(upcoming.length);
    }).catch(console.error);

    clubsApi.getClubRecentActivity(club.id).then(activities => {
      setRecentActivity(activities);
    }).catch(console.error);
  }, [club.id]);

  if (!club) return null;

  const stats = [
    {
      label: 'Total Members',
      value: membersCount || club.members || 0,
      icon: 'mdi:account-group',
      color: 'var(--primary)',
      show: true
    },
    {
      title: 'Announcements',
      path: 'announcements',
      icon: dashboardIcons.announcements,
      color: 'var(--orange)',
      desc: 'View and post club announcements'
    },
    {
      label: 'Upcoming Events',
      value: eventsCount,
      icon: 'mdi:calendar-clock',
      color: 'var(--gold)',
      show: true
    },
    {
      label: 'Pending Requests',
      value: pendingCount,
      icon: 'mdi:account-clock',
      color: 'var(--destructive)',
      show: canManageMembers(userRole)
    },
    {
      label: 'Active Tasks',
      value: tasksCount,
      icon: 'mdi:clipboard-check',
      color: 'var(--foreground)',
      show: true
    }
  ].filter(stat => stat.show);

  const quickActions = [
    {
      label: 'Post Announcement',
      icon: 'mdi:bullhorn-outline',
      description: 'Share news with members',
      show: canPostAnnouncement(userRole),
      action: () => navigate(`${basePath}/announcements`)
    },
    {
      label: 'Create Event',
      icon: 'mdi:calendar-plus',
      description: 'Schedule a new activity',
      show: canManageEvents(userRole),
      action: () => navigate(`${basePath}/events`)
    },
    {
      label: 'Review Requests',
      icon: 'mdi:account-plus-outline',
      description: 'Manage new applications',
      show: canManageMembers(userRole),
      action: () => navigate(`${basePath}/requests`)
    },
    {
      label: 'Assign Tasks',
      icon: 'mdi:checkbox-marked-circle-plus-outline',
      description: 'Delegate club work',
      show: canManageTasks(userRole),
      action: () => navigate(`${basePath}/manage-tasks`)
    }
  ].filter(action => action.show);

  // Fallback values for role presentation if util functions are not yet fully implemented
  const roleColor = getRoleColor ? getRoleColor(userRole) : 'var(--primary)';
  const roleIcon = getRoleIcon ? getRoleIcon(userRole) : 'mdi:account';
  const roleLabel = getRoleLabel ? getRoleLabel(userRole) : userRole;

  return (
    <div className={layoutStyles.workspaceArea} style={{ overflowY: 'auto' }}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Welcome back to {club.name}</h1>
          <p className={styles.subtitle}>Here's what's happening in your club today.</p>
        </div>
        {userRole && (
          <div
            className={styles.roleBadge}
            style={{
              '--role-color': roleColor,
              backgroundColor: `color-mix(in srgb, var(--role-color) 15%, transparent)`,
              color: 'var(--role-color)'
            }}
          >
            <Icon icon={roleIcon} className={styles.roleIcon} />
            <span>{roleLabel}</span>
          </div>
        )}
      </div>

      <div className={styles.statsGrid}>
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.label}
            value={stat.value}
            icon={stat.icon}
            color={stat.color}
          />
        ))}
      </div>

      <div className={styles.gridContainer}>
        <div className={styles.mainColumn}>
          {quickActions.length > 0 && (
            <section className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>Quick Actions</h2>
              </div>
              <div className={styles.actionsGrid}>
                {quickActions.map((action, index) => (
                  <button key={index} className={styles.actionCard} onClick={action.action}>
                    <div className={styles.actionIconWrapper}>
                      <Icon icon={action.icon} />
                    </div>
                    <div className={styles.actionContent}>
                      <h3>{action.label}</h3>
                      <p>{action.description}</p>
                    </div>
                    <Icon icon={uiIcons.chevronRight} className={styles.actionArrow} />
                  </button>
                ))}
              </div>
            </section>
          )}

          {/*
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Recent Activity</h2>
            </div>
            <div className={styles.activityFeed}>
              {recentActivity.length > 0 ? recentActivity.map(a => (
                <div key={a.id} className={styles.activityItem}>
                  <div className={styles.activityDot} style={{ backgroundColor: a.color }} />
                  <div className={styles.activityContent}>
                    <p>{a.text}</p>
                    <span className={styles.activityTime}>{a.time}</span>
                  </div>
                </div>
              )) : (
                <EmptyState 
                  icon={uiIcons.timelineTextOutline} 
                  title="No recent activity" 
                  description={`No recent activity in ${club.name}`} 
                />
              )}
            </div>
          </section>
          */}
        </div>

        <div className={styles.sideColumn}>
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Club Overview</h2>
            </div>
            <div className={styles.card}>
              {(club.banner_url || club.banner) && (
                <div className={styles.miniBanner} style={{ backgroundImage: `url(${club.banner_url || club.banner})`}} />
              )}
              <div className={styles.clubDetails}>
                <p><strong>Category:</strong> {club.category}</p>
                <p><strong>Status:</strong> {club.status}</p>
                <p><strong>University:</strong> {club.university?.name || 'University'}</p>
              </div>
            </div>
          </section>
        </div>
        </div>
      </div>
    </div>
  );
};
