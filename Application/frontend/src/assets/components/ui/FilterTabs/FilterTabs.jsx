import styles from './FilterTabs.module.css';

export const FilterTabs = ({ tabs, activeTab, onTabChange }) => {
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
