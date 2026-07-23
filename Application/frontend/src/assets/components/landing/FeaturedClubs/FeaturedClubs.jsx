import React from 'react';
import { Link } from 'react-router-dom';
import styles from './FeaturedClubs.module.css';
import { motion } from 'framer-motion';
import { Icon } from '@iconify/react';
import { SectionHeader } from '../SectionHeader/SectionHeader';
import { ClubCard } from '../../ui/ClubCard/ClubCard';
import { useSession } from '../../../../context/SessionContext';
import { authApi } from '@api/authApis/auth';

const bannerModules = import.meta.glob('../../../images/clubs/*.png', { eager: true, import: 'default' });
import { landingIcons } from '../../../icons/registry';

const findBanner = (keyword) => {
  const match = Object.keys(bannerModules).find(k => k.includes(keyword));
  return match ? bannerModules[match] : Object.values(bannerModules)[0] || '';
};

const baseClubs = [
  { name: 'Mind & Body Alliance', category: 'Wellness', members: 310, awards: 6, icon: landingIcons.clubMentalHealth, event: 'Mental Health Week', bannerKeyword: 'mental_health' },
  { name: 'Cultural Club', category: 'Arts', members: 260, awards: 12, icon: landingIcons.clubCultural, event: 'Nukkad Natak Competition', bannerKeyword: 'cultural' },
  { name: 'Music Society', category: 'Culture', members: 315, awards: 22, icon: landingIcons.clubMusic, event: 'Open Mic Friday', bannerKeyword: 'music' },
  { name: 'Coding Club', category: 'Engineering', members: 540, awards: 35, icon: landingIcons.clubCode, event: 'Web3 Workshop', bannerKeyword: 'coding' },
  { name: 'Culinary Club', category: 'Lifestyle', members: 220, awards: 10, icon: landingIcons.clubFood, event: 'Bake with us Day', bannerKeyword: 'food' },
];

const clubs = baseClubs.map((club) => ({
  ...club,
  image: findBanner(club.bannerKeyword)
}));

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
          actionLink={user ? authApi.getDashboardRoute(user.role) : "/register"}
        />
      </div>

      <div className={styles.marqueeWrapper}>
        <div className={styles.marqueeTrack}>
          {doubled.map((club, i) => (
            <ClubCard 
              key={i} 
              icon={club.icon}
              title={club.name}
              subtitle={`${club.members} members • ${club.awards} awards`}
              rightElement={club.category}
              bannerKeyword={club.bannerKeyword}
              onClick={() => window.location.href = user ? authApi.getDashboardRoute(user.role) : '/register'}
            />
          ))}
        </div>
      </div>
    </section>
  );
};
