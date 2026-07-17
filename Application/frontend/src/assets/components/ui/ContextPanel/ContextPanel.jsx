import React from 'react';
import styles from './ContextPanel.module.css';

export const ContextPanel = ({ children, className = '' }) => {
  return (
    <div className={`${styles.contextPanel} ${className}`}>
      <div className={styles.panelContainer}>
        {children}
      </div>
    </div>
  );
};
