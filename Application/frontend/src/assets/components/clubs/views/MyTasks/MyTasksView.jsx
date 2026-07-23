import React, { useMemo } from 'react';
import { Icon } from '@iconify/react';
import styles from './MyTasksView.module.css';
import layoutStyles from '../../../ui/ContextLayout/ContextLayout.module.css';
import { dashboardIcons, uiIcons } from '../../../../icons/registry';

const getStatusBadge = (status) => {
  const s = status?.toLowerCase();
  switch (s) {
    case 'assigned':
      return <span className={`${styles.badge} ${styles.badgeAssigned}`}>Assigned</span>;
    case 'in_progress':
      return <span className={`${styles.badge} ${styles.badgeInProgress}`}>In Progress</span>;
    case 'pending_review':
      return <span className={`${styles.badge} ${styles.badgeReview}`}>In Review</span>;
    case 'completed':
      return <span className={`${styles.badge} ${styles.badgeCompleted}`}>Completed</span>;
    case 'missed':
      return <span className={`${styles.badge} ${styles.badgeMissed}`}>Missed</span>;
    default:
      return null;
  }
};

const TaskCard = ({ task, onUpdateStatus }) => {
  const s = task.status?.toLowerCase();
  const isOverdue = new Date(task.due_at) < new Date() && s !== 'completed';
  const dueDate = new Date(task.due_at).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <div className={styles.taskCard}>
      <div className={styles.taskHeader}>
        <div className={styles.taskEvent}>
          <Icon icon={dashboardIcons.calendarStar} className={styles.eventIcon} />
          {task.event?.title || 'General Task'}
        </div>
        {getStatusBadge(task.status)}
      </div>

      <p className={styles.taskDescription}>{task.task_description}</p>

      <div className={styles.taskMeta}>
        <div className={styles.metaItem}>
          <Icon icon={uiIcons.accountArrowRight} />
          <span>Assigned by {task.assigner?.full_name || 'Admin'}</span>
        </div>
        <div className={`${styles.metaItem} ${isOverdue ? styles.overdue : ''}`}>
          <Icon icon={uiIcons.clockOutline} />
          <span>Due: {dueDate}</span>
        </div>
      </div>

      <div className={styles.taskActions}>
        {s === 'assigned' && (
          <button 
            className={`${styles.actionButton} ${styles.btnPrimary}`}
            onClick={() => onUpdateStatus(task.id, 'in_progress')}
          >
            <Icon icon={uiIcons.play} />
            Start Working
          </button>
        )}
        {s === 'in_progress' && (
          <button 
            className={`${styles.actionButton} ${styles.btnSuccess}`}
            onClick={() => onUpdateStatus(task.id, 'pending_review')}
          >
            <Icon icon={uiIcons.checkCircle} />
            Submit for Review
          </button>
        )}
        {s === 'pending_review' && (
          <span className={styles.pendingReviewNote}>
             Waiting for approval...
          </span>
        )}
      </div>
    </div>
  );
};

const MyTasksView = ({ club, userRole, tasks = [], onUpdateStatus, loading }) => {
  const { activeTasks, completedTasks } = useMemo(() => {
    const active = [];
    const completed = [];
    
    tasks.forEach(task => {
      const s = task.status?.toLowerCase();
      if (s === 'assigned' || s === 'in_progress' || s === 'pending_review') {
        active.push(task);
      } else {
        completed.push(task);
      }
    });

    return { activeTasks: active, completedTasks: completed };
  }, [tasks]);

  const handleUpdateStatus = async (taskId, newStatus) => {
    try {
      await onUpdateStatus(taskId, newStatus);
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  if (loading) {
    return (
      <div className={layoutStyles.workspaceArea}>
        <div className={layoutStyles.workspaceContent}>
          <div className={layoutStyles.header}>
            <h2 className={layoutStyles.title}>My Tasks</h2>
          </div>
          <div className={styles.skeletonGrid}>
            {[1, 2, 3].map(i => (
              <div key={i} className={styles.skeletonCard} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={layoutStyles.workspaceArea}>
      <div className={layoutStyles.workspaceContent}>
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>My Tasks</h2>
            <p className={styles.subtitle}>
              You have {activeTasks.length} active tasks
            </p>
          </div>
        </div>

        <div className={styles.content}>
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>
            <Icon icon={uiIcons.clipboardTextPlay} className={styles.sectionIcon} />
            Active Tasks
            <span className={styles.countBadge}>{activeTasks.length}</span>
          </h3>
          
          {activeTasks.length === 0 ? (
            <div className={styles.emptyState}>
              <Icon icon={uiIcons.checkAll} className={styles.emptyIcon} />
              <p>You're all caught up! No active tasks.</p>
            </div>
          ) : (
            <div className={styles.taskGrid}>
              {activeTasks.map(task => (
                <TaskCard 
                  key={task.id} 
                  task={task} 
                  onUpdateStatus={handleUpdateStatus} 
                />
              ))}
            </div>
          )}
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>
            <Icon icon={dashboardIcons.history} className={styles.sectionIcon} />
            Completed / Past
            <span className={styles.countBadge}>{completedTasks.length}</span>
          </h3>

          {completedTasks.length === 0 ? (
            <div className={styles.emptyState}>
              <Icon icon={dashboardIcons.history} className={styles.emptyIcon} />
              <p>No past tasks found.</p>
            </div>
          ) : (
            <div className={styles.taskGrid}>
              {completedTasks.map(task => (
                <TaskCard 
                  key={task.id} 
                  task={task} 
                  onUpdateStatus={handleUpdateStatus} 
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
    </div>
  );
};

export { MyTasksView };

