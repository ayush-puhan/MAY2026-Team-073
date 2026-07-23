import React, { useMemo } from 'react';
import styles from './ClubCard.module.css';
import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';

const bannerModules = import.meta.glob('../../../images/clubs/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : '';
};

export const ClubCard = ({ icon = 'mdi:account-group-outline', color = 'var(--accent)', title, subtitle, rightElement, university, onClick, bannerKeyword, bannerUrl, interests = [] }) => {
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

  const bannerStyle = bannerImg
    ? { backgroundImage: `url(${bannerImg})`, backgroundSize: 'cover', backgroundPosition: 'center' }
    : { background: `linear-gradient(135deg, color-mix(in oklab, ${color} 25%, var(--card)), color-mix(in oklab, ${color} 10%, var(--surface)))` };

  return (
    <div className={styles.card} onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
      <div 
        className={styles.banner} 
        style={{ 
          ...bannerStyle,
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
              <span key={idx}><Icon icon={idx === 0 ? "mdi:account-multiple-outline" : idx === 1 ? "mdi:tag-outline" : "mdi:star-outline"} /> {part}</span>
            ))}
          </div>
        )}
        {interests && interests.length > 0 && (
          <div className={styles.interestsRow}>
            {interests.map((interest, idx) => (
              <span key={idx} className={styles.interestTag}>
                {interest}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
