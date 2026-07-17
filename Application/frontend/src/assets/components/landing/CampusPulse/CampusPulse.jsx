import React from 'react';
import styles from './CampusPulse.module.css';
import { motion, useScroll, useTransform } from 'framer-motion';
import { landingIcons } from '../../../../assets/icons/registry';
import { Icon } from '@iconify/react';
import { SectionHeader } from '../SectionHeader/SectionHeader';
import { PulseCard } from '../../ui/PulseCard/PulseCard';

const pulseItems = [
  { icon: landingIcons.pulseCode, color: 'var(--innovation)', text: 'Hackathon registrations open', time: '2h ago' },
  { icon: landingIcons.pulseCamera, color: 'var(--campus-orange)', text: 'Photography contest tomorrow', time: '4h ago' },
  { icon: landingIcons.pulseRobot, color: 'var(--primary)', text: 'Robotics Club recruiting', time: '6h ago' },
  { icon: landingIcons.pulseBrain, color: 'var(--soft-purple)', text: 'AI Workshop — 30 seats left', time: 'Today' },
  { icon: landingIcons.pulseVolunteer, color: 'var(--achievement)', text: 'Volunteer opportunity available', time: 'Today' },
  { icon: landingIcons.pulseCertificate, color: 'var(--gold)', text: 'New certificates available', time: '1d ago' },
  { icon: landingIcons.pulseMusic, color: 'var(--campus-orange)', text: 'Open Mic Night — 12 spots left', time: 'Tomorrow' },
  { icon: landingIcons.pulseLightning, color: 'var(--gold)', text: 'Startup pitch competition', time: '3d' },
];


export const CampusPulse = () => {
  // Duplicate items for seamless looping
  const items = [...pulseItems, ...pulseItems];

  return (
    <section className={styles.section} id="events">
      <div className={styles.container}>
        <SectionHeader 
          label="CAMPUS PULSE"
          title="Something is"
          titleAccent="always happening."
          subtitle="Live updates from across the campus community."
          actionText="See all events"
          actionLink="/register"
        />
      </div>

      {/* Marquee row 1 — scrolls left */}
      <div className={styles.marqueeWrapper}>
        <div className={styles.marqueeTrack}>
          {items.map((item, i) => (
            <PulseCard key={`r1-${i}`} {...item} />
          ))}
        </div>
      </div>

      {/* Marquee row 2 — scrolls right */}
      <div className={styles.marqueeWrapper}>
        <div className={`${styles.marqueeTrack} ${styles.reverse}`}>
          {[...items].reverse().map((item, i) => (
            <PulseCard key={`r2-${i}`} {...item} />
          ))}
        </div>
      </div>
    </section>
  );
};
