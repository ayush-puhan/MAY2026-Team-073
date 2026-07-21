import React from 'react';
import styles from './AtmosphericHero.module.css';

export const AtmosphericHero = ({ name, quote }) => {
  const dateStr = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  const hour = new Date().getHours();
  const timeGreeting = hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Evening';

  return (
    <div className={styles.hero}>
      <span className={styles.date}>{dateStr}</span>
      <h1 className={styles.greeting}>Good {timeGreeting}{name ? `, ${name}` : ''}</h1>
      {quote && <p className={styles.quote}>{quote}</p>}
    </div>
  );
};
