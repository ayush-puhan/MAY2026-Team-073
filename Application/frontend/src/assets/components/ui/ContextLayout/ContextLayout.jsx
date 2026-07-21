import React from 'react';
import styles from './ContextLayout.module.css';

export const ContextLayout = ({ children, colorBlindMode = false }) => {
  return (
    <div className={`${styles.layoutContainer} ${colorBlindMode ? styles.colorBlind : ''}`}>
      {children}
    </div>
  );
};

