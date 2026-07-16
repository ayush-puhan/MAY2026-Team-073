import React from 'react';
import { Icon } from '@iconify/react';
import styles from './EmptyState.module.css';

export const EmptyState = ({ icon = 'mdi:inbox-outline', title, description }) => (
  <div className={styles.emptyState}>
    <Icon icon={icon} className={styles.icon} />
    {title && <p className={styles.title}>{title}</p>}
    {description && <p className={styles.description}>{description}</p>}
  </div>
);
