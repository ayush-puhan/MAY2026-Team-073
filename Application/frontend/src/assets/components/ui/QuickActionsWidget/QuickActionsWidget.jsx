import React from 'react';
import { Icon } from '@iconify/react';
import styles from './QuickActionsWidget.module.css';

export const QuickActionsWidget = ({ actions = [] }) => {
  return (
    <div className={styles.widgetCard}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Icon icon="mdi:flash-outline" width="20" />
          Quick Actions
        </h3>
      </div>
      <div className={styles.content}>
        <div className={styles.grid}>
          {actions.map((action, idx) => (
            <button 
              key={idx} 
              className={styles.actionBtn} 
              onClick={action.onClick}
            >
              <div className={styles.iconWrapper} style={{ color: action.color || 'var(--primary)' }}>
                <Icon icon={action.icon} width="28" />
              </div>
              <span className={styles.actionLabel}>{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
