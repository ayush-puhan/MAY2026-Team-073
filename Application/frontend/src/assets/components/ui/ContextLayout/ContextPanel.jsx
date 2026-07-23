import React from 'react';
import { NavLink } from 'react-router-dom';
import { Icon } from '@iconify/react';
import styles from './ContextLayout.module.css';

export const ContextPanel = ({ children, title }) => {
  return (
    <aside className={styles.contextPanel}>
      {title && <h2 className={styles.panelTitle}>{title}</h2>}
      <div className={styles.panelContent}>
        {children}
      </div>
    </aside>
  );
};

export const ContextPanelSection = ({ title, children }) => (
  <div className={styles.panelSection}>
    {title && <h3 className={styles.sectionTitle}>{title}</h3>}
    <div className={styles.sectionContent}>
      {children}
    </div>
  </div>
);

export const ContextPanelLink = ({ to, icon, label, exact = false, badge = null, onClick = null }) => (
  <NavLink 
    to={to} 
    end={exact}
    className={({ isActive }) => `${styles.panelLink} ${isActive ? styles.active : ''}`}
    onClick={onClick}
  >
    {icon && <span className={styles.linkIcon}><Icon icon={icon} /></span>}
    <span className={styles.linkLabel}>{label}</span>
    {badge != null && <span className={styles.linkBadge}>{badge}</span>}
  </NavLink>
);
