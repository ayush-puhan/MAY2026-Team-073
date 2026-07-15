import React from 'react';
import { Icon } from '@iconify/react';
import styles from './StatCard.module.css';

export const StatCard = ({ title, value, icon, color = 'var(--primary)', trend, trendLabel }) => (
  <div className={styles.card}>
    <div className={styles.iconWrapper} style={{ backgroundColor: `${color}15`, color }}>
      <Icon icon={icon} />
    </div>
    <div className={styles.content}>
      <p className={styles.title}>{title}</p>
      <p className={styles.value}>{value}</p>
      {trend !== undefined && trend !== null && (
        <p className={styles.trend}>
          <span className={trend >= 0 ? styles.trendUp : styles.trendDown}>
            <Icon icon={trend >= 0 ? 'mdi:arrow-up' : 'mdi:arrow-down'} />
            {Math.abs(trend)}%
          </span>
          {trendLabel && <span className={styles.trendLabel}>{trendLabel}</span>}
        </p>
      )}
    </div>
  </div>
);
