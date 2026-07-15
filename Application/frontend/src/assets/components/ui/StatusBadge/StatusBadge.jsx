import styles from './StatusBadge.module.css';

export const StatusBadge = ({ status }) => {
  const getStyles = () => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'approved':
      case 'open':
      case 'resolved':
        return { backgroundColor: 'var(--badge-success-bg)', color: 'var(--badge-success-text)' };
      case 'inactive':
      case 'closed':
      case 'rejected':
      case 'suspended':
        return { backgroundColor: 'var(--badge-error-bg)', color: 'var(--badge-error-text)' };
      case 'pending':
      case 'in progress':
      case 'assigned':
        return { backgroundColor: 'var(--badge-warning-bg)', color: 'var(--badge-warning-text)' };
      default:
        return { backgroundColor: 'var(--badge-info-bg)', color: 'var(--badge-info-text)' };
    }
  };

  return (
    <span className={styles.badge} style={getStyles()}>
      {status}
    </span>
  );
};
