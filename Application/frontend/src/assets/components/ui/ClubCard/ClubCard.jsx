import React from 'react';
import { Link } from 'react-router-dom';
import styles from './ClubCard.module.css';
import { Icon } from '@iconify/react';
import { landingIcons } from '../../../icons/registry';

export const ClubCard = ({ club, onJoin }) => (
  <div className={styles.card}>
    <div className={styles.banner} style={{ backgroundImage: `url(${club.image})`, backgroundSize: 'cover', backgroundPosition: 'center' }}>
      <div className={styles.categoryPill}>{club.category}</div>
      <div className={styles.iconCircle}>
        <Icon icon={club.icon} />
      </div>
    </div>
    <div className={styles.cardBody}>
      <h3>{club.name}</h3>
      <div className={styles.statsRow}>
        <span><Icon icon={landingIcons.accountOutline} /> {club.members}</span>
        <span><Icon icon={landingIcons.trophyOutline} /> {club.awards} awards</span>
      </div>
      <div className={styles.upcomingBox}>
        <span className={styles.upcomingLabel}>UPCOMING</span>
        <span className={styles.upcomingEvent}>{club.event}</span>
      </div>
      {typeof onJoin === 'function' ? (
        <button onClick={onJoin} className={styles.joinBtn}>
          Join club <Icon icon={landingIcons.arrowRight} />
        </button>
      ) : (
        <Link to={onJoin || '/register'} className={styles.joinBtn}>
          Join club <Icon icon={landingIcons.arrowRight} />
        </Link>
      )}
    </div>
  </div>
);
