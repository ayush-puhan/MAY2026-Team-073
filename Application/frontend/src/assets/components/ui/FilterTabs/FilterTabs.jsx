import React from 'react';
import clsx from 'clsx';
import styles from './FilterTabs.module.css';

// tabs: [{ value, label, count }]
export const FilterTabs = ({ tabs = [], activeTab, onTabChange }) => (
  <div className={styles.tabs}>
    {tabs.map((tab) => (
      <button
        key={tab.value}
        type="button"
        className={clsx(styles.tab, activeTab === tab.value && styles.active)}
        onClick={() => onTabChange(tab.value)}
      >
        {tab.label}
        {tab.count !== undefined && <span className={styles.count}>{tab.count}</span>}
      </button>
    ))}
  </div>
);
