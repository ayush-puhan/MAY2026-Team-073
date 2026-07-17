import React from 'react';
import styles from './PulseCard.module.css';
import { Icon } from '@iconify/react';

export const PulseCard = ({ icon, color, text, time }) => (
  <div className={styles.card}>
    <div className={styles.cardIcon} style={{ color, backgroundColor: `color-mix(in oklab, ${color} 12%, transparent)` }}>
      <Icon icon={icon} />
    </div>
    <span className={styles.cardText}>{text}</span>
    <span className={styles.cardTime}>{time}</span>
  </div>
);
