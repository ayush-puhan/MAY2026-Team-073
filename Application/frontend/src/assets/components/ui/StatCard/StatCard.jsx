import styles from './StatCard.module.css';
import { Icon } from '@iconify/react';

export const StatCard = ({ title, value, icon, trend, trendLabel, color = 'var(--primary)' }) => {
  const isPositive = trend > 0;
  
  return (
    <div className={styles.statCard}>
      <div className={styles.statHeader}>
        <h3 className={styles.statTitle}>{title}</h3>
        <div className={styles.iconWrapper} style={{ backgroundColor: `${color}15`, color }}>
          <Icon icon={icon} width="24" height="24" />
        </div>
      </div>
      <div className={styles.statBody}>
        <div className={styles.statValue}>{value}</div>
        {trend !== undefined && (
          <div className={styles.trendContainer}>
            <span className={isPositive ? styles.trendPositive : styles.trendNegative}>
              <Icon icon={isPositive ? 'mdi:arrow-up' : 'mdi:arrow-down'} width="16" />
              {Math.abs(trend)}%
            </span>
            {trendLabel && <span className={styles.trendLabel}>{trendLabel}</span>}
          </div>
        )}
      </div>
    </div>
  );
};
