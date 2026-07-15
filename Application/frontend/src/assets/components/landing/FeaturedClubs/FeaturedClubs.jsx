import React from 'react';
import { Link } from 'react-router-dom';
import styles from './FeaturedClubs.module.css';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { SectionHeader } from '../SectionHeader/SectionHeader';
import { ClubCard } from '../../ui/ClubCard/ClubCard';
import { useSession, getDashboardLink } from '../../../../context/SessionContext';

import mentalHealthBanner from '../../../images/mental_health_banner.png';
import culturalBanner from '../../../images/cultural_banner.png';
import musicBanner from '../../../images/music_banner.png';
import codingBanner from '../../../images/coding_banner.png';
import foodBanner from '../../../images/food_banner.png';
import { landingIcons } from '../../../icons/registry';

const clubs = [
  { name: 'Mind & Body Alliance', category: 'Wellness', members: 310, awards: 6, image: mentalHealthBanner, icon: landingIcons.clubMentalHealth, event: 'Mental Health Week' },
  { name: 'Cultural Club', category: 'Arts', members: 260, awards: 12, image: culturalBanner, icon: landingIcons.clubCultural, event: 'Nukkad Natak Competition' },
  { name: 'Music Society', category: 'Culture', members: 315, awards: 22, image: musicBanner, icon: landingIcons.clubMusic, event: 'Open Mic Friday' },
  { name: 'Coding Club', category: 'Engineering', members: 540, awards: 35, image: codingBanner, icon: landingIcons.clubCode, event: 'Web3 Workshop' },
  { name: 'Culinary Club', category: 'Lifestyle', members: 220, awards: 10, image: foodBanner, icon: landingIcons.clubFood, event: 'Bake with us Day' },
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
          actionLink={user ? getDashboardLink(user.role) : "/register"}
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
