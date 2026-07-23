import React, { useMemo } from 'react';
import { Icon } from '@iconify/react';
import styles from './AnnouncementDetailModal.module.css';
import { uiIcons, landingIcons } from '../../../../icons/registry';

const clubBannersModules = import.meta.glob('../../../../images/clubs/*.png', { eager: true, import: 'default' });
const clubBanners = Object.values(clubBannersModules);

const uniBannersModules = import.meta.glob('../../../../images/university/*.png', { eager: true, import: 'default' });
const uniBanners = Object.values(uniBannersModules);

const systemBannersModules = import.meta.glob('../../../../images/system/*.png', { eager: true, import: 'default' });
const systemBanners = Object.values(systemBannersModules);

const allBanners = { ...clubBannersModules, ...uniBannersModules, ...systemBannersModules };

export const AnnouncementDetailModal = ({ announcement, onClose }) => {
  if (!announcement) return null;

  const bannerImg = useMemo(() => {
    // If the announcement has a specific banner keyword, use it!
    if (announcement.banner) {
       const match = Object.keys(allBanners).find(k => k.includes(announcement.banner));
       if (match) return allBanners[match];
    }
    
    // Otherwise fallback if we are sure it needs a banner, but user said "optional".
    // If it's a university or system announcement, if no banner keyword is set, return empty.
    if (announcement.club_name === 'University-Wide' || announcement.club_name === 'System Admin' || announcement.posted_by_role === 'system_admin') {
      return ''; // No banner by default for these unless explicitly provided
    }

    // For regular clubs, we can fallback to the random club banner if they don't have one
    if (clubBanners.length === 0) return '';
    const titleSum = (announcement.title || '').split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return clubBanners[titleSum % clubBanners.length];
  }, [announcement]);

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        {bannerImg ? (
          <div 
            className={styles.banner}
            style={{ backgroundImage: `url(${bannerImg})` }}
          >
            <div className={styles.bannerOverlay}></div>
            <button className={styles.closeBtn} onClick={onClose}>
              <Icon icon={uiIcons.close} />
            </button>
          </div>
        ) : (
          <div className={styles.headerNoBanner}>
            <button className={styles.closeBtnDark} onClick={onClose}>
              <Icon icon={uiIcons.close} />
            </button>
          </div>
        )}
        
        <div className={styles.content}>
          <div className={styles.header}>
            <div className={styles.tags}>
              <span className={styles.clubTag}>
                {(announcement.club_name === 'University-Wide' || announcement.club_name === 'System-Wide') ? (
                  <Icon icon={uiIcons.bank} className={styles.tagIcon} />
                ) : (
                  <Icon icon={landingIcons.accountGroup} className={styles.tagIcon} />
                )}
                {announcement.club_name}
              </span>
              <span className={styles.date}>{new Date(announcement.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}</span>
            </div>
            <h2 className={styles.title}>{announcement.title}</h2>
          </div>
          
          <div className={styles.body}>
            {announcement.body.split('\n').map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
