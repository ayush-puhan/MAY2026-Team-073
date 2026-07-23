import React from 'react';
import { Icon } from '@iconify/react';
import { dashboardIcons, uiIcons } from '../../../icons/registry';
import styles from './DiscoverClubs.module.css';

const bannerModules = import.meta.glob('../../../images/clubs/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

export const DiscoverClubs = () => {
  const getBanner = (title = '') => {
    if (banners.length === 0) return '';
    const sum = (title || '').toString().split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return banners[sum % banners.length];
  };

  const clubs = [
    { id: 1, name: 'Google Developer Student Club', category: 'Tech', members: 120 },
    { id: 2, name: 'Robotics Society', category: 'Engineering', members: 85 },
    { id: 3, name: 'Debate Club', category: 'Arts', members: 45 },
  ];

  return (
    <div className={styles.widgetCard}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Icon icon={dashboardIcons.discover} width="20" />
          Discover Clubs
        </h3>
        <button className={styles.viewAll}>Explore <Icon icon={uiIcons.arrowRight} /></button>
      </div>
      <div className={styles.content}>
        <div className={styles.clubList}>
          {clubs.map(club => (
            <div key={club.id} className={styles.clubItem}>
              <div className={styles.clubImg} style={{ backgroundImage: `url(${getBanner(club.name)})` }}></div>
              <div className={styles.clubInfo}>
                <p className={styles.clubName}>{club.name}</p>
                <div className={styles.clubMeta}>
                  <span>{club.category}</span>
                  <span>â€¢</span>
                  <span><Icon icon={dashboardIcons.accountGroupOutline} /> {club.members}</span>
                </div>
              </div>
              <button className={styles.joinBtn}>Join</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

