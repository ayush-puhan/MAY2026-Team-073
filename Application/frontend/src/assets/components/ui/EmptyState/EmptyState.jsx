import { Icon } from '@iconify/react';
import { uiIcons } from '../../../icons/registry';
import styles from './EmptyState.module.css';

export const EmptyState = ({ title, description, icon = uiIcons.folderOpen }) => {
  return (
    <div className={styles.container}>
      <div className={styles.iconWrapper}>
        <Icon icon={icon} width="32" height="32" />
      </div>
      <div>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.description}>{description}</p>
      </div>
    </div>
  );
};
