import React from 'react';
import clsx from 'clsx';
import styles from './StatusBadge.module.css';

// Maps a status string to a badge variant. Pass an explicit `variant` to override.
const DEFAULT_STATUS_VARIANTS = {
  approved: 'success',
  active: 'success',
  resolved: 'success',
  submitted: 'warning',
  pending: 'warning',
  scheduled: 'info',
  rejected: 'error',
  inactive: 'neutral',
  closed: 'neutral',
};

export const StatusBadge = ({ status, variant, label }) => {
  const resolvedVariant = variant || DEFAULT_STATUS_VARIANTS[String(status).toLowerCase()] || 'neutral';
  const text = label || (typeof status === 'string'
    ? status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : status);

  return (
    <span className={clsx(styles.badge, styles[resolvedVariant])}>
      {text}
    </span>
  );
};
