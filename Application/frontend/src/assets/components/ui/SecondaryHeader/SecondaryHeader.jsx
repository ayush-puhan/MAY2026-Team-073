import React from 'react';
import { Icon } from '@iconify/react';
import styles from './SecondaryHeader.module.css';
import { uiIcons } from '../../../icons/registry';

export const SecondaryHeader = ({ title, description, tabs = [], activeTab, onTabChange, searchQuery, onSearchChange, searchPlaceholder = "Search...", rightControls }) => {
  return (
    <div className={styles.secondaryHeader}>
      <div className={styles.headerLeft}>
        {title && <h2 className={styles.title}>{title}</h2>}
        {description && <p className={styles.description}>{description}</p>}
        {tabs && tabs.length > 0 && (
          <div className={styles.headerTabs}>
            {tabs.map((tab, idx) => (
              <button 
                key={idx}
                className={`${styles.headerTab} ${activeTab === tab.id ? styles.active : ''}`}
                onClick={() => onTabChange(tab.id)}
              >
                {tab.icon && <Icon icon={tab.icon} className={styles.tabIcon} />}
                {tab.label}
              </button>
            ))}
          </div>
        )}
      </div>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        {rightControls}
        {onSearchChange && (
          <div className={styles.searchWrapper}>
            <Icon icon={uiIcons.magnify} className={styles.searchIcon} />
            <input 
              type="text" 
              placeholder={searchPlaceholder} 
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

