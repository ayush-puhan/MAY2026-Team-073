import React, { useMemo } from 'react';
import styles from './EventCard.module.css';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';

const bannerModules = import.meta.glob('../../../images/events/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : '';
};

export const EventCard = ({ icon = 'mdi:calendar-blank-outline', color = 'var(--primary)', title, subtitle, rightElement, university, onClick, bannerKeyword, bannerUrl }) => {
  const bannerImg = useMemo(() => {
    if (bannerUrl) return bannerUrl;
    if (bannerKeyword) {
      const specificBanner = findBanner(bannerKeyword);
      if (specificBanner) return specificBanner;
    }
    if (banners.length === 0) return '';
    const titleSum = (title || '').split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return banners[titleSum % banners.length];
  }, [title, bannerKeyword, bannerUrl]);

  return (
    <div className={styles.card} onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
      <div 
        className={styles.banner} 
        style={{ 
          backgroundImage: `url(${bannerImg})`, 
          backgroundSize: 'cover', 
          backgroundPosition: 'center',
          '--banner-color': `color-mix(in oklab, ${color} 15%, transparent)` 
        }}
      >
        <div className={styles.bannerBg}></div>
        {university && (
          <div className={styles.universityTag}>
            <Icon icon={uiIcons.schoolOutline} /> {university}
          </div>
        )}
        {rightElement && (
          <div className={styles.categoryPill}>
            {rightElement}
          </div>
        )}
        <div className={styles.iconCircle}>
          <Icon icon={icon} style={{ color }} />
        </div>
      </div>
      <div className={styles.cardBody}>
        <h3>{title}</h3>
        {subtitle && (
          <div className={styles.statsRow}>
            {subtitle.split(' • ').map((part, idx) => (
              <span key={idx}><Icon icon={idx === 0 ? "mdi:account-group-outline" : idx === 1 ? "mdi:map-marker-outline" : "mdi:clock-outline"} /> {part}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
