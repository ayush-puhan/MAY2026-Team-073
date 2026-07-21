import React from 'react';
import styles from './WelcomeBanner.module.css';

export const WelcomeBanner = ({ name, isGuest, quote }) => {
  const date = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  
  return (
    <div className={styles.banner}>
      <div className={styles.content}>
        <div className={styles.headerRow}>
          <div className={styles.titleArea}>
            <span className={styles.date}>{date}</span>
            <h1 className={styles.greeting}>Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening'}, {name}</h1>
            <p className={styles.quote}>{quote}</p>
          </div>
        </div>
        
        <div className={styles.metricsRow}>
          <div className={styles.metric}>
            <div className={styles.metricDot} style={{ background: 'var(--blue)' }} />
            <span><strong>2</strong> Events Today</span>
          </div>
          <div className={styles.metric}>
            <div className={styles.metricDot} style={{ background: 'var(--orange)' }} />
            <span>Reg closes in <strong>4 hours</strong></span>
          </div>
          <div className={styles.metric}>
            <div className={styles.metricDot} style={{ background: 'var(--purple)' }} />
            <span><strong>3</strong> New Announcements</span>
          </div>
        </div>
      </div>
      <div className={styles.bgIllustration}></div>
    </div>
  );
};
