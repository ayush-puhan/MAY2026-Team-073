import React from 'react';
import styles from './ThemeToggle.module.css';
import { Icon } from '@iconify/react';
import { useTheme } from '../../../../context/ThemeContext';

export const ThemeToggle = ({ className }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      id="theme-toggle-btn"
      className={`${styles.toggle} ${className || ''}`}
      onClick={toggleTheme}
      aria-label="Toggle theme"
    >
      <Icon icon={theme === 'dark' ? 'mdi:weather-night' : 'mdi:white-balance-sunny'} />
    </button>
  );
};