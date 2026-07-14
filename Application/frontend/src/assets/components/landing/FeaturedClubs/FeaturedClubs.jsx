import React from 'react';
import { Link } from 'react-router-dom';
import styles from './FeaturedClubs.module.css';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { SectionHeader } from '../SectionHeader/SectionHeader';
import { ClubCard } from '../../ui/ClubCard/ClubCard';
import { useSession, getDashboardLink } from '../../../../context/SessionContext';

import roboticsBanner from '../../../images/robotics_banner.png';
import cameraBanner from '../../../images/camera_banner.png';
import musicBanner from '../../../images/music_banner.png';
import codingBanner from '../../../images/coding_banner.png';
import financeBanner from '../../../images/finance_banner.png';
import { landingIcons } from '../../../icons/registry';

const clubs = [
  { name: 'Robotics Club', category: 'Engineering', members: 420, awards: 18, image: roboticsBanner, icon: landingIcons.clubRobot, event: 'Autonomous bot demo' },
  { name: 'Camera Club', category: 'Arts', members: 260, awards: 12, image: cameraBanner, icon: landingIcons.clubCamera, event: 'Street photo walk' },
  { name: 'Music Society', category: 'Culture', members: 315, awards: 22, image: musicBanner, icon: landingIcons.clubMusic, event: 'Open Mic Friday' },
  { name: 'Coding Club', category: 'Engineering', members: 540, awards: 35, image: codingBanner, icon: landingIcons.clubCode, event: 'Web3 Workshop' },
  { name: 'Finance Cell', category: 'Business', members: 180, awards: 8, image: financeBanner, icon: landingIcons.clubFinance, event: 'Mock Trading Session' },
];


export const FeaturedClubs = () => {
  const { user } = useSession();
  
  // Duplicate for seamless marquee
  const doubled = [...clubs, ...clubs, ...clubs];

  return (
    <section className={styles.section} id="clubs">
      <div className={styles.container}>
        <SectionHeader 
          label="FEATURED CLUBS"
          title="Communities"
          titleAccent="worth joining."
          subtitle="Drag, browse, hover. 72 active clubs across engineering, arts, sport, entrepreneurship and more."
          actionText="See all clubs"
          actionLink="/register"
        />
      </div>

      <div className={styles.marqueeWrapper}>
        <div className={styles.marqueeTrack}>
          {doubled.map((club, i) => (
            <ClubCard 
              key={i} 
              club={club} 
              onJoin={user ? getDashboardLink(user.role) : '/register'}
            />
          ))}
        </div>
      </div>
    </section>
  );
};
