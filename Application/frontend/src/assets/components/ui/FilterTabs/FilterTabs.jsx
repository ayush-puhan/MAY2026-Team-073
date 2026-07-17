import styles from './FilterTabs.module.css';
import { Dropdown } from '../Dropdown/Dropdown';
import { useState, useEffect } from 'react';

export const FilterTabs = ({ tabs, activeTab, onTabChange }) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (isMobile) {
    const options = tabs.map(tab => ({
      value: tab.id,
      label: tab.count !== undefined ? `${tab.label} (${tab.count})` : tab.label
    }));
    return (
      <div className={styles.mobileDropdownContainer}>
        <Dropdown
          options={options}
          value={activeTab}
          onChange={(e) => onTabChange(e.target.value)}
          className={styles.mobileDropdown}
        />
      </div>
    );
  }

  return (
    <div className={styles.tabsContainer}>
      {tabs.map((tab, idx) => (
        <button
          key={idx}
          className={`${styles.tabBtn} ${activeTab === tab.id ? styles.active : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={styles.tabCount}>{tab.count}</span>
          )}
        </button>
      ))}
    </div>
  );
};
