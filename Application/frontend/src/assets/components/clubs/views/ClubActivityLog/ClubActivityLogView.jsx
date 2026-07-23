import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Icon } from '@iconify/react';
import { clubsApi } from '../../../../../api/mockbackendApis/clubsApis/clubs';
import styles from './ClubActivityLogView.module.css';
import { EmptyState } from '../../../ui/EmptyState/EmptyState';
import { dashboardIcons, uiIcons, rewardsIcons } from '../../../../icons/registry';

const getActionIcon = (actionType) => {
  switch (actionType) {
    case 'MEMBERSHIP_CHANGE':
      return { icon: rewardsIcons.accountGroup, color: 'var(--blue)' };
    case 'TASK_UPDATE':
      return { icon: uiIcons.clipboardCheckOutline, color: 'var(--purple)' };
    case 'RESOURCE_UPLOAD':
      return { icon: uiIcons.folderOutline, color: 'var(--achievement)' };
    case 'COMMITTEE_CREATED':
      return { icon: 'mdi:account-multiple-plus', color: 'var(--gold)' };
    default:
      return { icon: 'mdi:history', color: 'var(--muted-foreground)' };
  }
};

const ClubActivityLogView = () => {
  const { club } = useOutletContext();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, [club.id]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await clubsApi.getClubAuditLogs(club.id);
      setLogs(data || []);
    } catch (err) {
      console.error(err);
      setError('Failed to load activity logs.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>Loading activity logs...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h2>Activity Log</h2>
        <p>Comprehensive audit log of all club activities, visible only to leadership.</p>
      </header>

      {logs.length === 0 ? (
        <EmptyState 
          icon="mdi:text-box-search-outline" 
          title="No activities recorded" 
          description="There are no audit logs available for this club yet." 
        />
      ) : (
        <div className={styles.logList}>
          {logs.map(log => {
            const { icon, color } = getActionIcon(log.action);
            return (
              <div key={log.id} className={styles.logCard}>
                <div className={styles.iconWrapper} style={{ backgroundColor: `color-mix(in srgb, ${color} 15%, transparent)`, color }}>
                  <Icon icon={icon} />
                </div>
                <div className={styles.logContent}>
                  <h4>{log.action.replace(/_/g, ' ')}</h4>
                  <p>{log.details}</p>
                  <div className={styles.logMeta}>
                    <span className={styles.metaItem}>
                      <Icon icon="mdi:account" /> {log.user?.first_name} {log.user?.last_name}
                    </span>
                    <span className={styles.metaItem}>
                      <Icon icon="mdi:clock-outline" /> {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ClubActivityLogView;
