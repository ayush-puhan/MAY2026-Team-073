import styles from './PriorityBadge.module.css';

export const PriorityBadge = ({ priority }) => {
  const displayPriority = priority || 'Medium';
  const getStyles = () => {
    switch (displayPriority.toLowerCase()) {
      case 'low':
        return { backgroundColor: 'var(--badge-info-bg)', color: 'var(--badge-info-text)' };
      case 'medium':
        return { backgroundColor: 'var(--badge-warning-bg)', color: 'var(--badge-warning-text)' };
      case 'high':
        return { backgroundColor: 'var(--badge-error-bg)', color: 'var(--badge-error-text)' };
      case 'critical':
        return { backgroundColor: 'var(--badge-critical-bg)', color: 'var(--badge-critical-text)' };
      default:
        return { backgroundColor: 'var(--badge-info-bg)', color: 'var(--badge-info-text)' };
    }
  };

  return (
    <span className={styles.badge} style={getStyles()}>
      {displayPriority}
    </span>
  );
};
