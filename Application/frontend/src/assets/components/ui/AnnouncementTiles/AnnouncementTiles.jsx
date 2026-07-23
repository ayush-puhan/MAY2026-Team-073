import React from 'react';
import { Icon } from '@iconify/react';
import styles from './AnnouncementTiles.module.css';
import { uiIcons } from '../../../icons/registry';

export const AnnouncementTiles = ({ announcements = [] }) => {
  if (!announcements || announcements.length === 0) return null;

  return (
    <div className={styles.tilesSection}>
      <div className={styles.headerRow}>
        <h3 className={styles.sectionTitle}>Campus Updates</h3>
      </div>
      
      <div className={styles.masonryGrid}>
        {announcements.map((ann, idx) => {
          const isLarge = ann.pinned;
          return (
            <div key={ann.id || idx} className={`  `}>
              <div className={styles.tileHeader}>
                <div className={styles.tags}>
                  <span className={styles.deptTag}>{ann.department || 'General'}</span>
                  {ann.urgent && <span className={styles.urgentTag}><Icon icon={uiIcons.alert} /> Urgent</span>}
                </div>
                {ann.pinned && <Icon icon={uiIcons.pin} className={styles.pinIcon} />}
              </div>
              
              <div className={styles.tileContent}>
                <h4 className={styles.tileTitle}>{ann.title}</h4>
                {isLarge && <p className={styles.tilePreview}>{ann.preview || 'Click to view the full details of this important update.'}</p>}
              </div>

              <div className={styles.tileFooter}>
                <span className={styles.tileTime}>{ann.time || 'Recently'}</span>
                <button className={styles.readMoreBtn}><Icon icon={uiIcons.arrowRight} /></button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
