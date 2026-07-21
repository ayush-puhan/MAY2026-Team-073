import React from 'react';
import { Icon } from '@iconify/react';
import styles from './RecentActivity.module.css';

export const RecentActivity = () => {
  const activities = [
    { id: 1, type: 'announcement', text: 'Computer Science Club posted an announcement', time: '10m ago', icon: 'mdi:bullhorn-outline', color: 'var(--orange)' },
    { id: 2, type: 'registration', text: 'You registered for Campus Clean-up', time: '2h ago', icon: 'mdi:ticket-confirmation-outline', color: 'var(--green)' },
    { id: 3, type: 'certificate', text: 'Web3 Workshop certificate released', time: '1d ago', icon: 'mdi:certificate-outline', color: 'var(--purple)' },
    { id: 4, type: 'event', text: 'New event added: Inter-College Chess', time: '2d ago', icon: 'mdi:calendar-plus', color: 'var(--blue)' },
  ];

  return (
    <div className={styles.widgetCard}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Icon icon="mdi:pulse" width="22" />
          Recent Activity
        </h3>
      </div>
      <div className={styles.content}>
        <div className={styles.feed}>
          {activities.map((item, idx) => (
            <div key={item.id} className={styles.feedItem}>
              <div className={styles.iconCircle} style={{ color: item.color, backgroundColor: color-mix(in oklab, $ 10%, transparent) }}>
                <Icon icon={item.icon} width="16" />
              </div>
              <div className={styles.itemInfo}>
                <p>{item.text}</p>
                <span>{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
