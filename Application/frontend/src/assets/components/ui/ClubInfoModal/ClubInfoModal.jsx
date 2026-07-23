import React, { useMemo } from 'react';
import styles from './ClubInfoModal.module.css';
import { Icon } from '@iconify/react';
import { uiIcons, dashboardIcons, landingIcons, authIcons } from '../../../icons/registry';

const bannerModules = import.meta.glob('../../../images/clubs/*.png', { eager: true, import: 'default' });
const banners = Object.values(bannerModules);

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : '';
};

export const ClubInfoModal = ({ club, onClose, onJoinClick, onOpenWorkspace }) => {
  if (!club) return null;

  const bannerImg = useMemo(() => {
    if (club.banner_url) return club.banner_url;
    const keyword = club.banner || club.category?.toLowerCase() || 'cultural';
    const specificBanner = findBanner(keyword);
    if (specificBanner) return specificBanner;
    
    if (banners.length === 0) return '';
    const titleSum = (club.name || '').split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return banners[titleSum % banners.length];
  }, [club]);

  // Derived status checks
  const isJoined = club.membership_status === 'approved';
  const isPending = club.membership_status === 'pending';

  const handleJoinClick = () => {
    if (isJoined || isPending) return;
    onJoinClick(club);
  };

  const universityName = club.university?.name || "Unknown University";

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          <Icon icon={uiIcons.close} />
        </button>
        <img 
          src={bannerImg} 
          alt={club.name} 
          className={styles.banner} 
        />
        
        <div className={styles.content}>
          <div className={styles.header}>
            <h2 className={styles.title}>{club.name}</h2>
            <div className={styles.clubInfo}>
              <span className={styles.clubName}>{club.category}</span>
              <span>•</span>
              <span>{universityName}</span>
            </div>
          </div>

          <div className={styles.detailsGrid}>
            <div className={styles.detailItem}>
              <Icon icon={landingIcons.accountGroup} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Members</h4>
                <p>{club.members || 0}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={dashboardIcons.calendarStar} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Founded</h4>
                <p>{club.founded_year || 'Unknown'}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={landingIcons.trophyOutline} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Awards</h4>
                <p>{club.awards || 0}</p>
              </div>
            </div>
            <div className={styles.detailItem}>
              <Icon icon={authIcons.emailOutline} className={styles.detailIcon} />
              <div className={styles.detailText}>
                <h4>Contact</h4>
                <p>{club.contact_email || 'N/A'}</p>
              </div>
            </div>
          </div>

          <div className={styles.description}>
            <h4>About the Club</h4>
            <p>{club.description || 'No description available.'}</p>
          </div>

          <div className={styles.footer}>
            {isJoined ? (
              <span className={`${styles.status} ${styles.completed}`}>Joined</span>
            ) : isPending ? (
              <span className={`${styles.status} ${styles.completed}`}>Pending Approval</span>
            ) : (
              <span className={styles.status}>Accepting Members</span>
            )}

            <div className={styles.footerActions}>
              {isJoined ? (
                <button 
                  className={styles.btnWorkspace}
                  onClick={() => onOpenWorkspace?.(club)}
                >
                  <Icon icon={uiIcons.arrowRightCircleOutline} />
                  View / Manage Club
                </button>
              ) : isPending ? (
                <button 
                  className={styles.btnRegister} 
                  disabled
                >
                  Requested
                </button>
              ) : (
                <button 
                  className={styles.btnRegister} 
                  onClick={handleJoinClick}
                >
                  Join Club
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
