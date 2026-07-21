import React from 'react';
import styles from './ContextLayout.module.css';

export const WorkspaceArea = ({ children, header }) => {
  return (
    <main className={styles.workspaceArea}>
      {header && <div className={styles.workspaceHeader}>{header}</div>}
      <div className={styles.workspaceContent}>
        {children}
      </div>
    </main>
  );
};
