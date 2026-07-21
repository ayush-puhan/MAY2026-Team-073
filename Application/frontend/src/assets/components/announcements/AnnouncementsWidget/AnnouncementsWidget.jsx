import React from 'react';
import { Icon } from '@iconify/react';
import { dashboardIcons } from '../../../../icons/registry';
import styles from './AnnouncementsWidget.module.css';

export const AnnouncementsWidget = ({ announcements = [] }) => {
  return (
    <div className={styles.widgetCard}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Icon icon={dashboardIcons.announcements} width="20" />
          Announcements
        </h3>
        <span className={styles.badge}>{announcements.length} New</span>
      </div>
      <div className={styles.content}>
        {announcements.length > 0 ? (
          <div className={styles.list}>
            {announcements.map((ann, idx) => (
              <div key={ann.id || idx} className={`  `}>
                <div className={styles.itemHeader}>
                  <div className={styles.itemMeta}>
                    <span className={styles.deptBadge}>{ann.department || 'General'}</span>
                    <span className={styles.itemTime}>{ann.time || 'Recently'}</span>
                  </div>
                  {ann.pinned && <Icon icon="mdi:pin" className={styles.pinIcon} />}
                </div>
                <p className={styles.itemTitle}>{ann.title}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className={styles.empty}>No new announcements.</p>
        )}
      </div>
    </div>
  );
};
