import React from 'react';
import { Icon } from '@iconify/react';
import styles from './SecondaryHeader.module.css';

export const SecondaryHeader = ({ tabs = [], activeTab, onTabChange, searchQuery, onSearchChange, searchPlaceholder = "Search..." }) => {
  return (
    <div className={styles.secondaryHeader}>
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
      <div className={styles.searchWrapper}>
        <Icon icon="mdi:magnify" className={styles.searchIcon} />
        <input 
          type="text" 
          placeholder={searchPlaceholder} 
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
    </div>
  );
};
