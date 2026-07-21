import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { rewardsIcons } from '../../../icons/registry';
import styles from './TaskCard.module.css';

export const TaskCard = ({ task, isCompleted, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);

  const handleComplete = async () => {
    setLoading(true);
    setVerifying(true);
    // Simulate verification delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    setVerifying(false);
    await onComplete(task);
    setLoading(false);
  };

  return (
    <div className={`${styles.card} ${isCompleted ? styles.completed : ''}`}>
      <div className={styles.iconWrapper}>
        <Icon icon={task.icon} className={styles.icon} />
      </div>
      
      <div className={styles.content}>
        <h4 className={styles.title}>{task.title}</h4>
        <p className={styles.desc}>{task.description}</p>
      </div>

      <div className={styles.actions}>
        <div className={styles.points}>
          <Icon icon={rewardsIcons.starFourPoints} className={styles.pointsIcon} />
          <span>{task.points}</span>
        </div>
        
        {isCompleted ? (
          <button className={styles.completedBtn} disabled>
            <Icon icon={rewardsIcons.checkCircle} /> Done
          </button>
        ) : (
          <button 
            className={styles.actionBtn} 
            onClick={handleComplete}
            disabled={loading}
          >
            {loading ? (
              <>
                <Icon icon="line-md:loading-twotone-loop" style={{ marginRight: '6px' }} /> 
                {verifying ? 'Verifying...' : 'Completing...'}
              </>
            ) : 'Complete'}
          </button>
        )}
      </div>
      
      {isCompleted && <div className={styles.checkmarkOverlay}><Icon icon={rewardsIcons.check} /></div>}
    </div>
  );
};
